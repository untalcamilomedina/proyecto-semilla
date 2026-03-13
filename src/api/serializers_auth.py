"""Custom JWT serializers for multitenant auth.

Includes tenant_id and role in JWT claims so the frontend
can resolve tenant context without extra API calls.
"""

from __future__ import annotations

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class TenantTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extend JWT tokens with tenant and role claims."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["email"] = user.email
        token["first_name"] = getattr(user, "first_name", "")
        token["last_name"] = getattr(user, "last_name", "")

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
