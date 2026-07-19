import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.models import TimeStampedModel


class User(AbstractUser):
    class Status(models.TextChoices):
        ACTIVE = "active", "正常"
        DISABLED = "disabled", "已禁用"
        LOCKED = "locked", "已锁定"
        PENDING_DELETE = "pending_delete", "待注销"
        DELETED = "deleted", "已删除"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nickname = models.CharField("昵称", max_length=80, blank=True)
    avatar_url = models.URLField("头像", blank=True)
    status = models.CharField("状态", max_length=24, choices=Status.choices, default=Status.ACTIVE)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.nickname or self.username


class UserPhone(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="phone")
    phone_ciphertext = models.TextField()
    phone_hash = models.CharField(max_length=64, unique=True, db_index=True)
    masked_phone = models.CharField(max_length=20)
    verified_at = models.DateTimeField()

    class Meta:
        db_table = "user_phones"


class UserIdentity(TimeStampedModel):
    class Provider(models.TextChoices):
        WECHAT_MINI_PROGRAM = "wechat_mini_program", "微信小程序"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="identities")
    provider = models.CharField(max_length=40, choices=Provider.choices)
    provider_app_id = models.CharField(max_length=100)
    provider_subject = models.CharField(max_length=160)
    unionid = models.CharField(max_length=160, blank=True)

    class Meta:
        db_table = "user_identities"
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_app_id", "provider_subject"],
                name="uniq_identity_provider_app_subject",
            )
        ]


class LoginEvent(TimeStampedModel):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    method = models.CharField(max_length=32)
    succeeded = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    failure_reason = models.CharField(max_length=120, blank=True)

    class Meta:
        db_table = "login_events"
        ordering = ["-created_at"]
