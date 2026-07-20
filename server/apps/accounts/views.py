from django.contrib.auth import get_user_model
from rest_framework import generics, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import LoginEvent
from .serializers import (
    ProfileSerializer,
    RegisterSerializer,
    UserSerializer,
    UserStatusSerializer,
)

User = get_user_model()


class PasswordTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.status != User.Status.ACTIVE:
            raise serializers.ValidationError("当前账号不可登录，请联系管理员。")
        request = self.context.get("request")
        LoginEvent.objects.create(
            user=self.user,
            method="password",
            succeeded=True,
            ip_address=request.META.get("REMOTE_ADDR") if request else None,
            user_agent=request.META.get("HTTP_USER_AGENT", "") if request else "",
        )
        return data


class LoginView(TokenObtainPairView):
    permission_classes = []
    serializer_class = PasswordTokenSerializer


class StatusAwareTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = self.token_class(attrs["refresh"])
        user_id = refresh[api_settings.USER_ID_CLAIM]
        user = User.objects.filter(
            **{api_settings.USER_ID_FIELD: user_id},
        ).first()
        if user is None or not user.is_active or user.status != User.Status.ACTIVE:
            raise AuthenticationFailed("当前账号不可登录，请联系管理员。")
        return super().validate(attrs)


class RefreshView(TokenRefreshView):
    permission_classes = []
    serializer_class = StatusAwareTokenRefreshSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        LoginEvent.objects.create(
            user=user,
            method="password_register",
            succeeded=True,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": ProfileSerializer(user).data,
            },
            status=201,
        )


class MeView(APIView):
    def get(self, request):
        return Response(ProfileSerializer(request.user).data)

    def patch(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MeCommentsView(generics.ListAPIView):
    def get_queryset(self):
        from apps.interactions.models import Comment

        return Comment.objects.filter(user=self.request.user).select_related("dish", "user")

    def get_serializer_class(self):
        from apps.interactions.serializers import CommentSerializer

        return CommentSerializer


class MeReportsView(generics.ListAPIView):
    def get_queryset(self):
        from apps.interactions.models import ContentReport

        return ContentReport.objects.filter(reporter=self.request.user).select_related(
            "reporter", "handled_by"
        )

    def get_serializer_class(self):
        from apps.interactions.serializers import ReportSerializer

        return ReportSerializer


class MeMealPlansView(generics.ListAPIView):
    def get_queryset(self):
        from apps.meal_plans.models import MealPlan

        return MealPlan.objects.filter(
            user=self.request.user, status=MealPlan.Status.SAVED
        ).prefetch_related("items__dish__category", "items__dish__tags", "items__recipe")

    def get_serializer_class(self):
        from apps.meal_plans.serializers import MealPlanSerializer

        return MealPlanSerializer


class AdminUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.prefetch_related("groups").select_related("phone")
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    search_fields = ["username", "nickname", "email"]
    filterset_fields = ["status", "is_staff"]
    ordering_fields = ["date_joined", "last_login", "username"]

    @action(detail=True, methods=["patch"], serializer_class=UserStatusSerializer)
    def status(self, request, pk=None):
        user = self.get_object()
        serializer = UserStatusSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(is_active=serializer.validated_data["status"] == User.Status.ACTIVE)
        return Response(UserSerializer(user).data)
