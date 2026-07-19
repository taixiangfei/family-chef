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


class PublicDishSerializer(DishListSerializer):
    recipe_id = serializers.SerializerMethodField()
    recipe_summary = serializers.SerializerMethodField()
    cooking_minutes = serializers.SerializerMethodField()
    difficulty = serializers.SerializerMethodField()
    servings = serializers.SerializerMethodField()

    class Meta(DishListSerializer.Meta):
        fields = DishListSerializer.Meta.fields + [
            "recipe_id",
            "recipe_summary",
            "cooking_minutes",
            "difficulty",
            "servings",
        ]

    def get_recipe(self, obj):
        try:
            article = obj.article
        except Exception:
            return None
        if article.status != "published":
            return None
        return article

    def get_recipe_id(self, obj):
        recipe = self.get_recipe(obj)
        return str(recipe.id) if recipe else None

    def get_recipe_summary(self, obj):
        recipe = self.get_recipe(obj)
        return recipe.current_version.summary if recipe and recipe.current_version else ""

    def get_cooking_minutes(self, obj):
        recipe = self.get_recipe(obj)
        return recipe.current_version.cooking_minutes if recipe and recipe.current_version else None

    def get_difficulty(self, obj):
        recipe = self.get_recipe(obj)
        return recipe.current_version.difficulty if recipe and recipe.current_version else None

    def get_servings(self, obj):
        recipe = self.get_recipe(obj)
        return recipe.current_version.servings if recipe and recipe.current_version else None


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
