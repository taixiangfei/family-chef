from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel
from apps.dishes.models import Dish


class Comment(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "待审核"
        VISIBLE = "visible", "可见"
        HIDDEN = "hidden", "已隐藏"
        REJECTED = "rejected", "已拒绝"
        DELETED = "deleted", "已删除"

    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    root = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="thread_replies"
    )
    content = models.TextField(max_length=2000)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)
    moderation_note = models.CharField(max_length=500, blank=True)
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moderated_comments",
    )
    moderated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "comments"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["dish", "status", "-created_at"])]


class DishReaction(TimeStampedModel):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=((1, "赞"), (-1, "踩")))

    class Meta:
        db_table = "dish_reactions"
        constraints = [
            models.UniqueConstraint(fields=["dish", "user"], name="uniq_user_dish_reaction"),
            models.CheckConstraint(
                condition=models.Q(value__in=[-1, 1]), name="dish_reaction_value_valid"
            ),
        ]


class CommentReaction(TimeStampedModel):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=((1, "赞"), (-1, "踩")))

    class Meta:
        db_table = "comment_reactions"
        constraints = [
            models.UniqueConstraint(
                fields=["comment", "user"], name="uniq_user_comment_reaction"
            ),
            models.CheckConstraint(
                condition=models.Q(value__in=[-1, 1]), name="comment_reaction_value_valid"
            ),
        ]


class ContentReport(TimeStampedModel):
    class TargetType(models.TextChoices):
        DISH = "dish", "菜品"
        COMMENT = "comment", "评论"

    class Status(models.TextChoices):
        PENDING = "pending", "待处理"
        RESOLVED = "resolved", "已处理"
        DISMISSED = "dismissed", "已驳回"

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    target_type = models.CharField(max_length=16, choices=TargetType.choices)
    target_id = models.UUIDField()
    reason = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    resolution = models.TextField(blank=True)
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="handled_reports",
    )

    class Meta:
        db_table = "content_reports"
        ordering = ["-created_at"]
