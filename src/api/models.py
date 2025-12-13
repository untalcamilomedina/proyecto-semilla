from __future__ import annotations

import secrets

from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone


class ApiKey(models.Model):
    organization = models.ForeignKey(
        "multitenant.Tenant", on_delete=models.CASCADE, related_name="api_keys"
    )
    user = models.ForeignKey(
        "core.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="api_keys"
    )
    name = models.CharField(max_length=120)
    prefix = models.CharField(max_length=12, unique=True)
    hashed_key = models.CharField(max_length=128)
    scopes = models.JSONField(default=list, blank=True)
    revoked_at = models.DateTimeField(blank=True, null=True)
    last_used_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None

    def check_secret(self, secret: str) -> bool:
        return self.is_active and check_password(secret, self.hashed_key)

    def mark_used(self) -> None:
        self.last_used_at = timezone.now()
        self.save(update_fields=["last_used_at"])

    @classmethod
    def generate(cls, *, organization, user, name: str, scopes: list[str] | None = None) -> tuple["ApiKey", str]:
        prefix = secrets.token_hex(4)
        secret = secrets.token_urlsafe(32)
        plain = f"ak_{prefix}_{secret}"
        obj = cls.objects.create(
            organization=organization,
            user=user,
            name=name,
            prefix=prefix,
            hashed_key=make_password(secret),
            scopes=scopes or [],
        )
        return obj, plain

