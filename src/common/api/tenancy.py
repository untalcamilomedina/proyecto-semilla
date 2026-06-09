"""Helpers compartidos para viewsets multitenant.

Reemplaza las copias locales de `request_tenant`/`TenantScopedViewSet`
que existían en lms, community y mcp.
"""

from __future__ import annotations

from rest_framework import viewsets
from rest_framework.exceptions import NotFound

from common.api.permissions import IsTenantMember


def request_tenant(request):
    return getattr(request, "tenant", None)


class TenantScopedViewSet(viewsets.GenericViewSet):
    """Base para viewsets de módulos: exige membresía en el tenant actual."""

    permission_classes = [IsTenantMember]

    def get_organization(self):
        organization = request_tenant(self.request)
        if organization is None:
            raise NotFound("Tenant required.")
        return organization
