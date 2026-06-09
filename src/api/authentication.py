from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework import authentication, exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication

from api.models import ApiKey


class TenantJWTAuthentication(JWTAuthentication):
    """JWT con binding al schema/tenant donde se emitió el token.

    Con usuarios por schema, los IDs colisionan entre tenants: un token del
    usuario id=N emitido en el schema A no debe autenticar como el usuario
    id=N del schema B. Si el token trae el claim `schema_name`, debe coincidir
    con el schema actual de la petición.
    """

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None
        user, validated_token = result

        token_schema = validated_token.get("schema_name")
        if token_schema:
            from multitenant.schema import get_current_schema

            current = get_current_schema()
            if token_schema != current:
                raise exceptions.AuthenticationFailed(
                    _("Token is not valid for this tenant."), code="tenant_mismatch"
                )
        return user, validated_token


class ApiKeyAuthentication(authentication.BaseAuthentication):
    # Use 'Api-Key' prefix to avoid conflict with JWT's 'Bearer' prefix.
    # Preferred: send API key as 'X-Api-Key: ak_xxx' header.
    # Alternative: 'Authorization: Api-Key ak_xxx'
    keyword = "Api-Key"
    header = "X-Api-Key"

    def authenticate(self, request) -> tuple[object, ApiKey] | None:
        raw = self._get_raw_key(request)
        if not raw:
            return None
        try:
            prefix, secret = self._split_key(raw)
        except ValueError:
            raise exceptions.AuthenticationFailed(_("Invalid API key format.")) from None

        try:
            key = ApiKey.objects.select_related("user", "organization").get(prefix=prefix)
        except ApiKey.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid API key.")) from None

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
                "description": (
                    "Use header `X-Api-Key: ak_<prefix>_<secret>` "
                    "(or `Authorization: Api-Key ak_<prefix>_<secret>`)."
                ),
            }

except Exception:  # pragma: no cover  # noqa: S110
    pass
