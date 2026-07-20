from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminUserViewSet,
    LoginView,
    MeCommentsView,
    MeMealPlansView,
    MeReportsView,
    MeView,
    RefreshView,
    RegisterView,
)

router = DefaultRouter()
router.register("admin/users", AdminUserViewSet, basename="admin-users")

urlpatterns = [
    path("auth/login/password/", LoginView.as_view(), name="password-login"),
    path("auth/register/", RegisterView.as_view(), name="password-register"),
    path("auth/token/refresh/", RefreshView.as_view(), name="token-refresh"),
    path("users/me/", MeView.as_view(), name="users-me"),
    path("users/me/comments/", MeCommentsView.as_view(), name="users-me-comments"),
    path("users/me/reports/", MeReportsView.as_view(), name="users-me-reports"),
    path("users/me/meal-plans/", MeMealPlansView.as_view(), name="users-me-meal-plans"),
    path("", include(router.urls)),
]
