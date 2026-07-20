from django.db import models

from apps.common.models import TimeStampedModel


class DishCategory(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "启用"
        DISABLED = "disabled", "停用"

    key = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=80)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="children"
    )
    sort_order = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        db_table = "dish_categories"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class Tag(TimeStampedModel):
    class Type(models.TextChoices):
        GENERAL = "general", "通用"
        METHOD = "method", "做法"
        SOURCE = "source", "来源"

    class Status(models.TextChoices):
        ACTIVE = "active", "启用"
        DISABLED = "disabled", "停用"

    name = models.CharField(max_length=80, unique=True)
    type = models.CharField(max_length=16, choices=Type.choices, default=Type.GENERAL)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        db_table = "tags"
        ordering = ["type", "name"]

    def __str__(self):
        return self.name


class Dish(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "草稿"
        PUBLISHED = "published", "已发布"
        UNPUBLISHED = "unpublished", "已下架"
        ARCHIVED = "archived", "已归档"

    legacy_id = models.CharField(max_length=80, unique=True, null=True, blank=True)
    name = models.CharField(max_length=160, db_index=True)
    slug = models.SlugField(max_length=180, unique=True)
    category = models.ForeignKey(
        DishCategory, on_delete=models.PROTECT, related_name="dishes"
    )
    tags = models.ManyToManyField(Tag, through="DishTag", related_name="dishes")
    cover_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    source_project = models.CharField(max_length=80, blank=True)
    source_path = models.CharField(max_length=500, blank=True)
    source_url = models.URLField(max_length=1000, blank=True)
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "dishes"
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["status", "category", "-updated_at"])]

    def __str__(self):
        return self.name


class DishTag(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT)

    class Meta:
        db_table = "dish_tags"
        constraints = [
            models.UniqueConstraint(fields=["dish", "tag"], name="uniq_dish_tag")
        ]
