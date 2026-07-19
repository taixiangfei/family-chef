from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminRecipeArticleViewSet, PublicRecipeDetailViewSet

router = DefaultRouter()
router.register("recipes", PublicRecipeDetailViewSet, basename="recipes")
router.register("admin/articles", AdminRecipeArticleViewSet, basename="admin-articles")

urlpatterns = [path("", include(router.urls))]
