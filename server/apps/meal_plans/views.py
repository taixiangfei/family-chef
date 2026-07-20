from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import MealPlan, MealPlanTemplate
from .serializers import (
    MealPlanGenerateSerializer,
    MealPlanSerializer,
    MealPlanTemplateSerializer,
)
from .services import ensure_default_templates, generate_meal_plan


class MealPlanTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MealPlanTemplateSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        ensure_default_templates()
        return MealPlanTemplate.objects.filter(status=MealPlanTemplate.Status.ACTIVE)


class MealPlanViewSet(viewsets.ModelViewSet):
    serializer_class = MealPlanSerializer
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        queryset = MealPlan.objects.select_related("user").prefetch_related(
            "items__dish__category", "items__dish__tags", "items__recipe"
        )
        if self.request.user.is_staff:
            return queryset
        if self.action == "retrieve":
            if self.request.user.is_authenticated:
                return queryset.filter(status=MealPlan.Status.DRAFT) | queryset.filter(
                    user=self.request.user
                )
            return queryset.filter(status=MealPlan.Status.DRAFT)
        if self.action == "save":
            return queryset.filter(status=MealPlan.Status.DRAFT) | queryset.filter(
                user=self.request.user
            )
        if self.action == "replace_item":
            if self.request.user.is_authenticated:
                return queryset.filter(status=MealPlan.Status.DRAFT) | queryset.filter(
                    user=self.request.user
                )
            return queryset.filter(status=MealPlan.Status.DRAFT)
        if self.request.user.is_authenticated:
            return queryset.filter(user=self.request.user, status=MealPlan.Status.SAVED)
        return queryset.none()

    def get_permissions(self):
        if self.action in {"generate", "retrieve", "replace_item"}:
            return [permissions.AllowAny()]
        if self.action in {"admin_list", "admin_templates"}:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["post"])
    def generate(self, request):
        serializer = MealPlanGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            plan = generate_meal_plan(serializer.validated_data, user=request.user, persist=False)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(plan).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def save(self, request, pk=None):
        plan = self.get_object()
        plan.user = request.user
        plan.status = MealPlan.Status.SAVED
        plan.save(update_fields=["user", "status", "updated_at"])
        return Response(self.get_serializer(plan).data)

    @action(detail=True, methods=["post"])
    def regenerate(self, request, pk=None):
        plan = self.get_object()
        data = {
            "mode": plan.mode,
            "themeKey": plan.theme_key,
            "servings": plan.servings,
            "mealType": plan.meal_type,
            "targetCount": plan.target_count,
            **(plan.preferences or {}),
        }
        data.update(request.data or {})
        try:
            new_plan = generate_meal_plan(
                data, user=request.user, persist=request.user.is_authenticated
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(new_plan).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path=r"items/(?P<item_id>[^/.]+)/replace")
    def replace_item(self, request, pk=None, item_id=None):
        plan = self.get_object()
        item = get_object_or_404(plan.items.all(), pk=item_id)
        data = {
            "mode": plan.mode,
            "themeKey": plan.theme_key,
            "servings": plan.servings,
            "mealType": plan.meal_type,
            "targetCount": 1,
            **(plan.preferences or {}),
            "excludeDishIds": [str(existing.dish_id) for existing in plan.items.all()],
            "seed": f"{plan.id}:{item.id}:{plan.updated_at.timestamp()}",
        }
        try:
            replacement_plan = generate_meal_plan(data, user=request.user, persist=False)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        replacement = replacement_plan.items.first()
        item.dish = replacement.dish
        item.recipe = replacement.recipe
        item.reason = replacement.reason
        item.snapshot = replacement.snapshot
        item.save(update_fields=["dish", "recipe", "reason", "snapshot", "updated_at"])
        replacement_plan.delete()

        plan_items = plan.items.select_related("dish__article__current_version")
        dishes = [plan_item.dish for plan_item in plan_items]
        plan.total_minutes = sum(
            dish.article.current_version.cooking_minutes
            for dish in dishes
            if hasattr(dish, "article") and dish.article.current_version
        )
        plan.save(update_fields=["total_minutes", "updated_at"])
        return Response(self.get_serializer(plan).data)

    def destroy(self, request, *args, **kwargs):
        plan = self.get_object()
        if plan.user_id != request.user.id and not request.user.is_staff:
            return Response({"detail": "只能删除自己的配菜方案。"}, status=403)
        plan.status = MealPlan.Status.ARCHIVED
        plan.save(update_fields=["status", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminMealPlanTemplateViewSet(viewsets.ModelViewSet):
    queryset = MealPlanTemplate.objects.all()
    serializer_class = MealPlanTemplateSerializer
    permission_classes = [permissions.IsAdminUser]
    search_fields = ["key", "name"]
    filterset_fields = ["status"]
    ordering_fields = ["sort_order", "created_at", "updated_at", "name"]

    def initial(self, request, *args, **kwargs):
        ensure_default_templates()
        super().initial(request, *args, **kwargs)


class AdminMealPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MealPlan.objects.select_related("user").prefetch_related(
        "items__dish__category", "items__dish__tags", "items__recipe"
    )
    serializer_class = MealPlanSerializer
    permission_classes = [permissions.IsAdminUser]
    search_fields = ["title", "user__username"]
    filterset_fields = ["mode", "theme_key", "status", "user"]
    ordering_fields = ["created_at", "updated_at", "total_minutes"]
