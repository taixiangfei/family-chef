from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
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


class ProfileSerializer(serializers.ModelSerializer):
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
            "roles",
            "phone",
            "last_login",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "username",
            "status",
            "roles",
            "phone",
            "last_login",
            "date_joined",
        ]

    def get_roles(self, obj):
        return list(obj.groups.values_list("name", flat=True))

    def get_phone(self, obj):
        phone = getattr(obj, "phone", None)
        return phone.masked_phone if phone else None


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "password_confirm", "nickname", "email"]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "两次输入的密码不一致。"})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            nickname=validated_data.get("nickname", ""),
            email=validated_data.get("email", ""),
            status=User.Status.ACTIVE,
        )
