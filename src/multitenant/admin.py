from __future__ import annotations

from django.contrib import admin

from .models import Domain, Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "schema_name", "is_active", "plan_code", "created_at")
    search_fields = ("name", "slug", "schema_name")


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "tenant", "is_primary")
    search_fields = ("domain",)
    list_filter = ("is_primary",)

