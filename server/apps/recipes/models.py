from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel
from apps.dishes.models import Dish


class RecipeArticle(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "草稿"
        PENDING_REVIEW = "pending_review", "待审核"
        REJECTED = "rejected", "已驳回"
        PUBLISHED = "published", "已发布"
        UNPUBLISHED = "unpublished", "已下架"

    dish = models.OneToOneField(Dish, on_delete=models.CASCADE, related_name="article")
    title = models.CharField(max_length=180)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.DRAFT)
    current_version = models.ForeignKey(
        "RecipeVersion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="published_for_articles",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="authored_articles",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_articles",
    )
    review_note = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "recipe_articles"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title


class RecipeVersion(TimeStampedModel):
    class Difficulty(models.TextChoices):
        EASY = "easy", "简单"
        BASIC = "basic", "基础"
        MEDIUM = "medium", "进阶"
        HARD = "hard", "困难"

    article = models.ForeignKey(RecipeArticle, on_delete=models.CASCADE, related_name="versions")
    version_no = models.PositiveIntegerField()
    summary = models.TextField(blank=True)
    cooking_minutes = models.PositiveIntegerField(default=20)
    difficulty = models.CharField(
        max_length=16,
        choices=Difficulty.choices,
        default=Difficulty.BASIC,
    )
    servings = models.PositiveSmallIntegerField(default=1)
    tips = models.JSONField(default=list, blank=True)
    change_note = models.CharField(max_length=240, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        db_table = "recipe_versions"
        ordering = ["-version_no"]
        constraints = [
            models.UniqueConstraint(
                fields=["article", "version_no"], name="uniq_article_version_no"
            )
        ]


class RecipeIngredient(TimeStampedModel):
    version = models.ForeignKey(RecipeVersion, on_delete=models.CASCADE, related_name="ingredients")
    name = models.CharField(max_length=160, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=40, blank=True)
    note = models.CharField(max_length=240, blank=True)
    raw_text = models.CharField(max_length=500)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "recipe_ingredients"
        ordering = ["sort_order", "created_at"]


class RecipeStep(TimeStampedModel):
    version = models.ForeignKey(RecipeVersion, on_delete=models.CASCADE, related_name="steps")
    description = models.TextField()
    image_url = models.URLField(blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "recipe_steps"
        ordering = ["sort_order", "created_at"]
