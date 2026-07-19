from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminUserViewSet, LoginView, MeView, RefreshView, RegisterView

router = DefaultRouter()
router.register("admin/users", AdminUserViewSet, basename="admin-users")

urlpatterns = [
    path("auth/login/password/", LoginView.as_view(), name="password-login"),
    path("auth/register/", RegisterView.as_view(), name="password-register"),
    path("auth/token/refresh/", RefreshView.as_view(), name="token-refresh"),
    path("users/me/", MeView.as_view(), name="users-me"),
    path("", include(router.urls)),
]
