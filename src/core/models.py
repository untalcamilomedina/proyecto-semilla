from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField("email address", unique=True)


class Permission(models.Model):
    module = models.CharField(max_length=50)
    codename = models.SlugField(max_length=120, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, default="")
    is_system = models.BooleanField(default=False)

    class Meta:
        ordering = ["module", "codename"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.module}:{self.codename}"


class Role(models.Model):
    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="roles"
    )
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80)
    description = models.TextField(blank=True, default="")
    position = models.PositiveIntegerField(default=0)
    is_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    permissions = models.ManyToManyField(Permission, through="RolePermission", related_name="roles")

    class Meta:
        unique_together = [("organization", "slug")]
        ordering = ["-position", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:80]
        return super().save(*args, **kwargs)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.organization.slug}:{self.name}"


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        unique_together = [("role", "permission")]


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="memberships")
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "organization")]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user_id}@{self.organization.slug}"


class RoleAuditLog(models.Model):
    class Action(models.TextChoices):
        CREATED = "created", _("created")
        UPDATED = "updated", _("updated")
        DELETED = "deleted", _("deleted")
        PERMS_CHANGED = "perms_changed", _("perms_changed")
        IMPORTED = "imported", _("imported")

    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="role_audits"
    )
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=Action.choices)
    before = models.JSONField(blank=True, null=True)
    after = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OnboardingState(models.Model):
    tenant = models.OneToOneField(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="onboarding_state"
    )
    owner_email = models.EmailField()
    current_step = models.PositiveSmallIntegerField(default=1)
    completed_steps = models.JSONField(default=list, blank=True)
    data = models.JSONField(default=dict, blank=True)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def mark_step_complete(self, step: int) -> None:
        if step not in self.completed_steps:
            self.completed_steps.append(step)
        self.current_step = max(self.current_step, step + 1)


class ActivityLog(models.Model):
    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="activity_logs"
    )
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    object_id = models.CharField(max_length=50, blank=True, null=True)
    object_repr = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "-created_at"]),
        ]
