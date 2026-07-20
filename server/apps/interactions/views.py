from django.db import transaction
from django.db.models import Count, F, Q
from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.dishes.models import Dish

from .models import Comment, CommentReaction, ContentReport, DishReaction
from .serializers import (
    CommentSerializer,
    ModerationSerializer,
    ReactionSerializer,
    ReportSerializer,
)


def update_reaction(model, target_field, target, user, value):
    lookup = {target_field: target, "user": user}
    if value == 0:
        model.objects.filter(**lookup).delete()
    else:
        model.objects.update_or_create(defaults={"value": value}, **lookup)


def sync_counts(target, reaction_model, target_field):
    counts = reaction_model.objects.filter(**{target_field: target}).aggregate(
        likes=Count("id", filter=Q(value=1)), dislikes=Count("id", filter=Q(value=-1))
    )
    target.like_count = counts["likes"]
    target.dislike_count = counts["dislikes"]
    target.save(update_fields=["like_count", "dislike_count", "updated_at"])


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        queryset = Comment.objects.select_related("user")
        if not self.request.user.is_staff:
            queryset = queryset.filter(status=Comment.Status.VISIBLE)
        dish_id = self.request.query_params.get("dish")
        return queryset.filter(dish_id=dish_id) if dish_id else queryset.none()

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        parent = serializer.validated_data.get("parent")
        root = parent.root or parent if parent else None
        comment = serializer.save(user=self.request.user, root=root)
        Dish.objects.filter(pk=comment.dish_id).update(comment_count=F("comment_count") + 1)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def reaction(self, request, pk=None):
        serializer = ReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = self.get_object()
        update_reaction(
            CommentReaction, "comment", comment, request.user, serializer.validated_data["value"]
        )
        sync_counts(comment, CommentReaction, "comment")
        return Response(CommentSerializer(comment).data)


class DishReactionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def create(self, request, dish_id=None):
        serializer = ReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dish = Dish.objects.get(pk=dish_id)
        update_reaction(
            DishReaction, "dish", dish, request.user, serializer.validated_data["value"]
        )
        sync_counts(dish, DishReaction, "dish")
        return Response({"likeCount": dish.like_count, "dislikeCount": dish.dislike_count})


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer

    def get_queryset(self):
        queryset = ContentReport.objects.select_related("reporter", "handled_by")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(reporter=self.request.user)

    def get_permissions(self):
        if self.action in {"list", "retrieve", "resolve"}:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        report = self.get_object()
        report.status = request.data.get("status", ContentReport.Status.RESOLVED)
        report.resolution = request.data.get("resolution", "")
        report.handled_by = request.user
        report.save()
        return Response(self.get_serializer(report).data)


class AdminCommentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Comment.objects.select_related("dish", "user", "moderated_by")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAdminUser]
    search_fields = ["content", "user__username", "dish__name"]
    filterset_fields = ["status", "dish"]

    @action(detail=True, methods=["post"])
    def moderate(self, request, pk=None):
        comment = self.get_object()
        serializer = ModerationSerializer(comment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(moderated_by=request.user, moderated_at=timezone.now())
        return Response(CommentSerializer(comment).data)
