from django.contrib import admin

from .models import MealPlan, MealPlanItem, MealPlanTemplate


class MealPlanItemInline(admin.TabularInline):
    model = MealPlanItem
    extra = 0
    readonly_fields = ["snapshot", "created_at", "updated_at"]


@admin.register(MealPlanTemplate)
class MealPlanTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "key", "status", "sort_order", "updated_at"]
    list_filter = ["status"]
    search_fields = ["name", "key"]


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "mode", "theme_key", "status", "total_minutes", "updated_at"]
    list_filter = ["mode", "theme_key", "status"]
    search_fields = ["title", "user__username"]
    inlines = [MealPlanItemInline]
