from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminMealPlanTemplateViewSet,
    AdminMealPlanViewSet,
    MealPlanTemplateViewSet,
    MealPlanViewSet,
)

router = DefaultRouter()
router.register("meal-plan-themes", MealPlanTemplateViewSet, basename="meal-plan-themes")
router.register("meal-plans", MealPlanViewSet, basename="meal-plans")
router.register(
    "admin/meal-plan-templates",
    AdminMealPlanTemplateViewSet,
    basename="admin-meal-plan-templates",
)
router.register("admin/meal-plans", AdminMealPlanViewSet, basename="admin-meal-plans")

urlpatterns = [path("", include(router.urls))]
