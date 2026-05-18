from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Issue, Comment


@admin.register(User)
class TrackerUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )
    list_display = ("username", "email", "role", "is_staff", "is_active")


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "priority", "status", "reporter", "assignee", "created_at")
    list_filter = ("status", "category", "priority")
    search_fields = ("title", "description")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("issue", "author", "created_at")
    search_fields = ("body",)
