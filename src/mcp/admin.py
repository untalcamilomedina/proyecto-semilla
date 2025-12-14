from __future__ import annotations

from django.contrib import admin

from .models import McpResource, McpServer, McpTool, McpUsageLog


@admin.register(McpServer)
class McpServerAdmin(admin.ModelAdmin):
    list_display = ("organization", "name", "endpoint_url", "is_active")
    list_filter = ("organization", "is_active")
    search_fields = ("name", "description", "endpoint_url")
    list_select_related = ("organization",)


@admin.register(McpTool)
class McpToolAdmin(admin.ModelAdmin):
    list_display = ("organization", "server", "name")
    list_filter = ("organization", "server")
    search_fields = ("name", "description", "server__name")
    list_select_related = ("organization", "server")


@admin.register(McpResource)
class McpResourceAdmin(admin.ModelAdmin):
    list_display = ("organization", "server", "uri", "name", "mime_type")
    list_filter = ("organization", "server", "mime_type")
    search_fields = ("uri", "name", "description", "server__name")
    list_select_related = ("organization", "server")


@admin.register(McpUsageLog)
class McpUsageLogAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ("organization", "created_at", "server", "tool", "user")
    list_filter = ("organization", "server", "tool", "created_at")
    search_fields = ("server__name", "tool__name", "user__email", "user__username")
    readonly_fields = ("created_at",)
    list_select_related = ("organization", "server", "tool", "user")

