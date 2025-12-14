from __future__ import annotations

from typing import Optional, Tuple

from django.utils.translation import gettext_lazy as _
from rest_framework import authentication, exceptions

from api.models import ApiKey


class ApiKeyAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"
    header = "X-Api-Key"

    def authenticate(self, request) -> Optional[Tuple[object, ApiKey]]:
        raw = self._get_raw_key(request)
        if not raw:
            return None
        try:
            prefix, secret = self._split_key(raw)
        except ValueError:
            raise exceptions.AuthenticationFailed(_("Invalid API key format."))

        try:
            key = ApiKey.objects.select_related("user", "organization").get(prefix=prefix)
        except ApiKey.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid API key."))

        if not key.check_secret(secret):
            raise exceptions.AuthenticationFailed(_("Invalid API key."))

        organization = getattr(request, "tenant", None)
        if organization is None:
            raise exceptions.AuthenticationFailed(_("Tenant required for API key authentication."))
        if key.organization_id != organization.id:
            raise exceptions.AuthenticationFailed(_("API key does not belong to this tenant."))

        key.mark_used()
        user = key.user
        if user is None:
            raise exceptions.AuthenticationFailed(_("API key not linked to a user."))
        return user, key

    def _get_raw_key(self, request) -> str | None:
        header_val = request.headers.get(self.header)
        if header_val:
            return header_val.strip()
        auth = request.headers.get("Authorization")
        if not auth:
            return None
        parts = auth.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            return None
        return parts[1].strip()

    def _split_key(self, raw: str) -> tuple[str, str]:
        if not raw.startswith("ak_"):
            raise ValueError
        _, prefix, secret = raw.split("_", 2)
        return prefix, secret


try:  # pragma: no cover
    from drf_spectacular.extensions import OpenApiAuthenticationExtension

    class ApiKeyAuthenticationScheme(OpenApiAuthenticationExtension):
        target_class = "api.authentication.ApiKeyAuthentication"
        name = "ApiKeyAuth"

        def get_security_definition(self, auto_schema):
            return {
                "type": "apiKey",
                "in": "header",
                "name": ApiKeyAuthentication.header,
                "description": "Use header `X-Api-Key: ak_<prefix>_<secret>` (or `Authorization: Bearer ak_<prefix>_<secret>`).",
            }
except Exception:  # pragma: no cover
    pass
