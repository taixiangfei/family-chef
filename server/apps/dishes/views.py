from django.db.models import Count
from rest_framework import permissions, viewsets

from .models import Dish, DishCategory, Tag
from .serializers import (
    CategorySerializer,
    DishListSerializer,
    DishWriteSerializer,
    TagSerializer,
)


class PublicCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DishCategory.objects.filter(status=DishCategory.Status.ACTIVE).annotate(
        dish_count=Count("dishes")
    )
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class PublicTagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.filter(status=Tag.Status.ACTIVE).annotate(dish_count=Count("dishes"))
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class PublicDishViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Dish.objects.filter(status=Dish.Status.PUBLISHED)
        .select_related("category")
        .prefetch_related("tags")
    )
    serializer_class = DishListSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ["name", "source_project", "tags__name"]
    filterset_fields = ["category", "tags"]
    ordering_fields = ["updated_at", "like_count", "comment_count", "name"]


class AdminCategoryViewSet(viewsets.ModelViewSet):
    queryset = DishCategory.objects.annotate(dish_count=Count("dishes"))
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]
    search_fields = ["key", "name"]
    filterset_fields = ["status"]


class AdminTagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.annotate(dish_count=Count("dishes"))
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAdminUser]
    search_fields = ["name"]
    filterset_fields = ["type", "status"]


class AdminDishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.select_related("category").prefetch_related("tags")
    permission_classes = [permissions.IsAdminUser]
    search_fields = ["name", "legacy_id", "source_project"]
    filterset_fields = ["status", "category", "tags"]
    ordering_fields = ["created_at", "updated_at", "name"]

    def get_serializer_class(self):
        if self.action in {"list", "retrieve"}:
            return DishListSerializer
        return DishWriteSerializer
