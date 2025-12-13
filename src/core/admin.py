from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Membership, OnboardingState, Permission, Role, RoleAuditLog, RolePermission, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    pass


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("module", "codename", "name", "is_system")
    search_fields = ("module", "codename", "name")
    list_filter = ("module", "is_system")


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 0
    autocomplete_fields = ("permission",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "organization", "position", "is_system")
    search_fields = ("name", "slug")
    list_filter = ("organization", "is_system")
    inlines = (RolePermissionInline,)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "role", "is_active", "joined_at")
    search_fields = ("user__email", "organization__slug")
    list_filter = ("organization", "role", "is_active")


@admin.register(RoleAuditLog)
class RoleAuditAdmin(admin.ModelAdmin):
    list_display = ("organization", "role", "action", "actor", "created_at")
    list_filter = ("organization", "action")


@admin.register(OnboardingState)
class OnboardingStateAdmin(admin.ModelAdmin):
    list_display = ("tenant", "owner_email", "current_step", "is_complete", "updated_at")
    list_filter = ("is_complete", "current_step")
