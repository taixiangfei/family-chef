from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import LoginEvent, User, UserIdentity, UserPhone


@admin.register(User)
class FamilyChefUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("家常主厨", {"fields": ("nickname", "avatar_url", "status")}),
    )
    list_display = ("username", "nickname", "status", "is_staff", "date_joined")
    list_filter = ("status", "is_staff", "is_superuser")


admin.site.register(UserPhone)
admin.site.register(UserIdentity)
admin.site.register(LoginEvent)
