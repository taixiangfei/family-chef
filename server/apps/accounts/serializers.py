from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "nickname",
            "avatar_url",
            "email",
            "status",
            "is_staff",
            "is_superuser",
            "roles",
            "phone",
            "last_login",
            "date_joined",
        ]
        read_only_fields = ["id", "last_login", "date_joined", "roles", "phone"]

    def get_roles(self, obj):
        return list(obj.groups.values_list("name", flat=True))

    def get_phone(self, obj):
        phone = getattr(obj, "phone", None)
        return phone.masked_phone if phone else None


class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["status"]
