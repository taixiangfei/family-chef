from rest_framework import serializers

from apps.dishes.models import Dish
from apps.dishes.serializers import TagSerializer

from .models import RecipeArticle, RecipeIngredient, RecipeStep, RecipeVersion


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ["id", "name", "quantity", "unit", "note", "raw_text", "sort_order"]
        read_only_fields = ["id"]


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeStep
        fields = ["id", "description", "image_url", "duration_seconds", "sort_order"]
        read_only_fields = ["id"]


class RecipeVersionSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    steps = StepSerializer(many=True)

    class Meta:
        model = RecipeVersion
        fields = [
            "id",
            "version_no",
            "summary",
            "cooking_minutes",
            "difficulty",
            "servings",
            "tips",
            "change_note",
            "ingredients",
            "steps",
            "created_at",
        ]
        read_only_fields = ["id", "version_no", "created_at"]


class RecipeArticleSerializer(serializers.ModelSerializer):
    dish_name = serializers.CharField(source="dish.name", read_only=True)
    current_version = RecipeVersionSerializer(read_only=True)
    version_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = RecipeArticle
        fields = [
            "id",
            "dish",
            "dish_name",
            "title",
            "status",
            "current_version",
            "version_count",
            "review_note",
            "published_at",
            "updated_at",
        ]
        read_only_fields = ["id", "current_version", "published_at", "updated_at"]


class AdminRecipeArticleSerializer(RecipeArticleSerializer):
    latest_version = serializers.SerializerMethodField()

    class Meta(RecipeArticleSerializer.Meta):
        fields = RecipeArticleSerializer.Meta.fields + ["latest_version"]

    def get_latest_version(self, obj):
        version = obj.versions.first()
        return RecipeVersionSerializer(version).data if version else None


class PublicDishSummarySerializer(serializers.ModelSerializer):
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
            "source_project",
            "source_path",
            "source_url",
            "like_count",
            "dislike_count",
            "comment_count",
        ]


class PublicRecipeArticleSerializer(RecipeArticleSerializer):
    dish = PublicDishSummarySerializer(read_only=True)
