"""Permisos DRF multitenant (ubicación canónica).

Deny-by-default: toda vista multitenant debe exigir membresía activa en el
tenant actual. `api.permissions` re-exporta estos símbolos por compatibilidad.
"""

from __future__ import annotations

from rest_framework.permissions import BasePermission

from common.policies import get_membership, has_permission


class IsTenantMember(BasePermission):
    """Exige usuario autenticado CON membresía activa en el tenant actual.

    Sin esta verificación, un usuario autenticado de otro tenant podría
    acceder a datos del tenant del host actual.
    """

    message = "You are not a member of this organization."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        organization = getattr(request, "tenant", None)
        if organization is None:
            return False
        if getattr(request.user, "is_superuser", False):
            return True
        return get_membership(request.user, organization) is not None


class PolicyPermission(BasePermission):
    """
    DRF permission that delegates to common.policies.

    Siempre exige membresía activa en el tenant actual (deny-by-default).
    Views may define additional required codenames:
    - permission_codename: str
    - permission_codenames: list[str]
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        organization = getattr(request, "tenant", None)
        if organization is None:
            return False
        is_superuser = getattr(request.user, "is_superuser", False)
        if not is_superuser and get_membership(request.user, organization) is None:
            return False
        codenames = []
        if hasattr(view, "permission_codenames"):
            codenames = list(view.permission_codenames or [])
        elif hasattr(view, "permission_codename"):
            codenames = [view.permission_codename]
        if not codenames:
            return True
        return all(has_permission(request.user, organization, code) for code in codenames)
