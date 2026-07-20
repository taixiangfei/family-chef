from django.contrib import admin

from .models import RecipeArticle, RecipeIngredient, RecipeStep, RecipeVersion


@admin.register(RecipeArticle)
class RecipeArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "dish", "status", "published_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("title", "dish__name")


admin.site.register(RecipeVersion)
admin.site.register(RecipeIngredient)
admin.site.register(RecipeStep)
