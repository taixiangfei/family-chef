from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import UserSerializer, UserStatusSerializer

User = get_user_model()


class LoginView(TokenObtainPairView):
    permission_classes = []


class RefreshView(TokenRefreshView):
    permission_classes = []


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


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
