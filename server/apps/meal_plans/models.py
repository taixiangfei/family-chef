from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel
from apps.dishes.models import Dish
from apps.recipes.models import RecipeArticle


class MealPlanTemplate(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "启用"
        DISABLED = "disabled", "停用"

    key = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    rules = models.JSONField(default=dict, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        db_table = "meal_plan_templates"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class MealPlan(TimeStampedModel):
    class Mode(models.TextChoices):
        CUSTOM = "custom", "自定义"
        THEME = "theme", "主题"
        RANDOM = "random", "随机"

    class MealType(models.TextChoices):
        BREAKFAST = "breakfast", "早餐"
        LUNCH = "lunch", "午餐"
        DINNER = "dinner", "晚餐"
        ALL_DAY = "all_day", "全天"

    class Status(models.TextChoices):
        DRAFT = "draft", "临时"
        SAVED = "saved", "已保存"
        ARCHIVED = "archived", "已归档"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="meal_plans",
    )
    title = models.CharField(max_length=160)
    mode = models.CharField(max_length=16, choices=Mode.choices)
    theme_key = models.CharField(max_length=80, blank=True)
    servings = models.PositiveSmallIntegerField(default=2)
    meal_type = models.CharField(
        max_length=16, choices=MealType.choices, default=MealType.DINNER
    )
    target_count = models.PositiveSmallIntegerField(default=4)
    preferences = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)
    total_minutes = models.PositiveIntegerField(default=0)
    shopping_list = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        db_table = "meal_plans"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "status", "-updated_at"]),
            models.Index(fields=["mode", "theme_key", "-created_at"]),
        ]

    def __str__(self):
        return self.title


class MealPlanItem(TimeStampedModel):
    plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name="items")
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT, related_name="meal_plan_items")
    recipe = models.ForeignKey(
        RecipeArticle, on_delete=models.PROTECT, related_name="meal_plan_items"
    )
    sort_order = models.PositiveIntegerField(default=0)
    reason = models.CharField(max_length=240, blank=True)
    snapshot = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "meal_plan_items"
        ordering = ["sort_order", "created_at"]
        constraints = [
            models.UniqueConstraint(fields=["plan", "dish"], name="uniq_meal_plan_dish")
        ]

    def __str__(self):
        return f"{self.plan} - {self.dish}"
