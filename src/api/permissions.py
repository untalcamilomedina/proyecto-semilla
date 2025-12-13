from __future__ import annotations

from rest_framework.permissions import BasePermission

from common.policies import has_permission


class PolicyPermission(BasePermission):
    """
    DRF permission that delegates to common.policies.

    Views may define:
    - permission_codename: str
    - permission_codenames: list[str]
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        organization = getattr(request, "tenant", None)
        if organization is None:
            return False
        codenames = []
        if hasattr(view, "permission_codenames"):
            codenames = list(getattr(view, "permission_codenames") or [])
        elif hasattr(view, "permission_codename"):
            codenames = [getattr(view, "permission_codename")]
        if not codenames:
            return True
        return all(has_permission(request.user, organization, code) for code in codenames)
