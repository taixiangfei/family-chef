from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminCategoryViewSet,
    AdminDishViewSet,
    AdminTagViewSet,
    PublicCategoryViewSet,
    PublicDishViewSet,
    PublicTagViewSet,
)

public_router = DefaultRouter()
public_router.register("categories", PublicCategoryViewSet, basename="categories")
public_router.register("tags", PublicTagViewSet, basename="tags")
public_router.register("dishes", PublicDishViewSet, basename="dishes")

admin_router = DefaultRouter()
admin_router.register("admin/categories", AdminCategoryViewSet, basename="admin-categories")
admin_router.register("admin/tags", AdminTagViewSet, basename="admin-tags")
admin_router.register("admin/dishes", AdminDishViewSet, basename="admin-dishes")

urlpatterns = [path("", include(public_router.urls)), path("", include(admin_router.urls))]
