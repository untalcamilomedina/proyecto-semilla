"""Custom JWT serializers for multitenant auth.

Includes tenant_id and role in JWT claims so the frontend
can resolve tenant context without extra API calls.

SEGURIDAD: el claim `schema_name` ata el token al schema donde se emitió.
Con usuarios por schema, los IDs de usuario colisionan entre tenants; sin
este claim, un token del usuario id=N del tenant A autenticaría como el
usuario id=N del tenant B. `TenantJWTAuthentication` lo verifica.
"""

from __future__ import annotations

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from multitenant.schema import get_current_schema


class TenantTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extend JWT tokens with tenant and role claims."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["email"] = user.email
        token["first_name"] = getattr(user, "first_name", "")
        token["last_name"] = getattr(user, "last_name", "")

        # Binding del token al schema donde se autenticó el usuario.
        token["schema_name"] = get_current_schema()

        # Attach tenant info from first active membership
        from core.models import Membership

        membership = (
            Membership.objects.filter(user=user, is_active=True)
            .select_related("organization", "role")
            .first()
        )
        if membership:
            token["tenant_id"] = membership.organization_id
            token["tenant_slug"] = membership.organization.slug
            token["role"] = membership.role.slug if membership.role else ""

        return token
