from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.db import models


SUBDOMAIN_RE = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")
RESERVED_SUBDOMAINS = {
    "www",
    "admin",
    "api",
    "static",
    "media",
    "mail",
    "cdn",
}


def validate_subdomain(value: str) -> None:
    if not SUBDOMAIN_RE.match(value):
        raise ValidationError("Invalid subdomain format.")
    if value in RESERVED_SUBDOMAINS:
        raise ValidationError("Subdomain is reserved.")


class Tenant(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=63, unique=True, help_text="Used as default subdomain.")
    schema_name = models.CharField(max_length=63, unique=True)
    is_active = models.BooleanField(default=True)
    plan_code = models.CharField(max_length=50, blank=True, default="")
    trial_ends_at = models.DateTimeField(blank=True, null=True)
    enabled_modules = models.JSONField(default=list, blank=True)
    branding = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self) -> None:
        validate_subdomain(self.slug)
        validate_subdomain(self.schema_name)

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Domain(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="domains")
    domain = models.CharField(max_length=255, unique=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Domain"
        verbose_name_plural = "Domains"

    def __str__(self) -> str:  # pragma: no cover
        return self.domain
