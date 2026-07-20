from rest_framework import serializers

from .models import Dish, DishCategory, Tag


class CategorySerializer(serializers.ModelSerializer):
    dish_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = DishCategory
        fields = ["id", "key", "name", "parent", "sort_order", "status", "dish_count"]


class TagSerializer(serializers.ModelSerializer):
    dish_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Tag
        fields = ["id", "name", "type", "status", "dish_count"]


class DishListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Dish
        fields = [
            "id",
            "legacy_id",
            "name",
            "slug",
            "category",
            "category_name",
            "tags",
            "cover_url",
            "status",
            "source_project",
            "like_count",
            "dislike_count",
            "comment_count",
            "updated_at",
        ]


class DishWriteSerializer(serializers.ModelSerializer):
    tag_ids = serializers.PrimaryKeyRelatedField(
        source="tags", queryset=Tag.objects.all(), many=True, required=False
    )

    class Meta:
        model = Dish
        fields = [
            "id",
            "legacy_id",
            "name",
            "slug",
            "category",
            "tag_ids",
            "cover_url",
            "status",
            "source_project",
            "source_path",
            "source_url",
        ]
        read_only_fields = ["id"]
