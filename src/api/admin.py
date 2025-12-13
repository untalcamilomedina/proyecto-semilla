from __future__ import annotations

from django.contrib import admin

from .models import ApiKey


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "prefix", "organization", "user", "revoked_at", "last_used_at", "created_at")
    search_fields = ("name", "prefix", "user__email")
    list_filter = ("organization", "revoked_at")

