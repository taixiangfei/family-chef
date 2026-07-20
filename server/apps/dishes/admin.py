from django.contrib import admin

from .models import Dish, DishCategory, DishTag, Tag


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "status", "source_project", "updated_at")
    list_filter = ("status", "category", "source_project")
    search_fields = ("name", "legacy_id")


admin.site.register(DishCategory)
admin.site.register(Tag)
admin.site.register(DishTag)
