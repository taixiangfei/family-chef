from rest_framework import serializers

from .models import MealPlan, MealPlanItem, MealPlanTemplate


class MealPlanTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPlanTemplate
        fields = [
            "id",
            "key",
            "name",
            "description",
            "rules",
            "sort_order",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MealPlanGenerateSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=MealPlan.Mode.choices, default=MealPlan.Mode.RANDOM)
    themeKey = serializers.CharField(required=False, allow_blank=True)
    servings = serializers.IntegerField(min_value=1, max_value=12, default=2)
    mealType = serializers.ChoiceField(
        choices=MealPlan.MealType.choices, default=MealPlan.MealType.DINNER
    )
    targetCount = serializers.IntegerField(min_value=1, max_value=8, default=4)
    categoryKeys = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )
    avoidKeywords = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )
    availableIngredients = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )
    maxMinutes = serializers.IntegerField(min_value=1, max_value=240, required=False)
    seed = serializers.CharField(required=False, allow_blank=True)


class MealPlanItemSerializer(serializers.ModelSerializer):
    dishId = serializers.UUIDField(source="dish_id", read_only=True)
    recipeId = serializers.UUIDField(source="recipe_id", read_only=True)
    name = serializers.SerializerMethodField()
    categoryName = serializers.SerializerMethodField()
    coverUrl = serializers.SerializerMethodField()
    cookingMinutes = serializers.SerializerMethodField()
    difficulty = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = MealPlanItem
        fields = [
            "id",
            "dishId",
            "recipeId",
            "name",
            "categoryName",
            "coverUrl",
            "cookingMinutes",
            "difficulty",
            "tags",
            "reason",
            "snapshot",
            "sort_order",
        ]

    def snapshot_value(self, obj, key, fallback=""):
        return obj.snapshot.get(key, fallback) if obj.snapshot else fallback

    def get_name(self, obj):
        return self.snapshot_value(obj, "name", obj.dish.name)

    def get_categoryName(self, obj):
        return self.snapshot_value(obj, "categoryName", obj.dish.category.name)

    def get_coverUrl(self, obj):
        return self.snapshot_value(obj, "coverUrl", obj.dish.cover_url)

    def get_cookingMinutes(self, obj):
        return self.snapshot_value(obj, "cookingMinutes", None)

    def get_difficulty(self, obj):
        return self.snapshot_value(obj, "difficulty", "")

    def get_tags(self, obj):
        return self.snapshot_value(obj, "tags", [])


class MealPlanSerializer(serializers.ModelSerializer):
    items = MealPlanItemSerializer(many=True, read_only=True)
    themeKey = serializers.CharField(source="theme_key", read_only=True)
    mealType = serializers.CharField(source="meal_type", read_only=True)
    targetCount = serializers.IntegerField(source="target_count", read_only=True)
    totalMinutes = serializers.IntegerField(source="total_minutes", read_only=True)
    shoppingList = serializers.JSONField(source="shopping_list", read_only=True)
    isSaved = serializers.SerializerMethodField()
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = MealPlan
        fields = [
            "id",
            "title",
            "mode",
            "themeKey",
            "servings",
            "mealType",
            "targetCount",
            "preferences",
            "summary",
            "totalMinutes",
            "shoppingList",
            "status",
            "isSaved",
            "username",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_isSaved(self, obj):
        return obj.status == MealPlan.Status.SAVED
