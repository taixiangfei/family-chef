from django.db import transaction
from django.db.models import Count, Max
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import RecipeArticle, RecipeVersion
from .serializers import RecipeArticleSerializer, RecipeVersionSerializer


class AdminRecipeArticleViewSet(viewsets.ModelViewSet):
    queryset = (
        RecipeArticle.objects.select_related("dish", "current_version")
        .prefetch_related("current_version__ingredients", "current_version__steps")
        .annotate(version_count=Count("versions"))
    )
    serializer_class = RecipeArticleSerializer
    permission_classes = [permissions.IsAdminUser]
    search_fields = ["title", "dish__name"]
    filterset_fields = ["status", "dish"]
    ordering_fields = ["created_at", "updated_at", "published_at"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def versions(self, request, pk=None):
        article = self.get_object()
        serializer = RecipeVersionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        next_version = (article.versions.aggregate(value=Max("version_no"))["value"] or 0) + 1
        ingredients = serializer.validated_data.pop("ingredients")
        steps = serializer.validated_data.pop("steps")
        version = RecipeVersion.objects.create(
            article=article,
            version_no=next_version,
            created_by=request.user,
            **serializer.validated_data,
        )
        version.ingredients.bulk_create(
            [version.ingredients.model(version=version, **item) for item in ingredients]
        )
        version.steps.bulk_create([version.steps.model(version=version, **item) for item in steps])
        return Response(RecipeVersionSerializer(version).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        article = self.get_object()
        article.status = RecipeArticle.Status.PENDING_REVIEW
        article.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(article).data)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def publish(self, request, pk=None):
        article = self.get_object()
        version_id = request.data.get("versionId")
        version = article.versions.get(pk=version_id) if version_id else article.versions.first()
        if version is None:
            return Response(
                {"detail": "请先创建教程版本。"}, status=status.HTTP_400_BAD_REQUEST
            )
        article.current_version = version
        article.reviewer = request.user
        article.status = RecipeArticle.Status.PUBLISHED
        article.published_at = timezone.now()
        article.review_note = request.data.get("reviewNote", "")
        article.save()
        article.dish.status = article.dish.Status.PUBLISHED
        article.dish.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(article).data)

    @action(detail=True, methods=["post"])
    def unpublish(self, request, pk=None):
        article = self.get_object()
        article.status = RecipeArticle.Status.UNPUBLISHED
        article.review_note = request.data.get("reviewNote", "")
        article.save(update_fields=["status", "review_note", "updated_at"])
        article.dish.status = article.dish.Status.UNPUBLISHED
        article.dish.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(article).data)


class PublicRecipeDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        RecipeArticle.objects.filter(status=RecipeArticle.Status.PUBLISHED)
        .select_related("dish", "dish__category", "current_version")
        .prefetch_related("dish__tags", "current_version__ingredients", "current_version__steps")
    )
    serializer_class = RecipeArticleSerializer
    permission_classes = [permissions.AllowAny]
