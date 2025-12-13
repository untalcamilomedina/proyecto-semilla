from __future__ import annotations

from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest
from django.views.generic.base import ContextMixin

from common.policies import get_membership, has_permission


class TenantPermissionMixin(ContextMixin):
    """
    Ensures request.tenant exists and (optionally) checks a policy permission.
    """

    permission_codename: str | None = None
    require_membership: bool = True

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        organization = getattr(request, "tenant", None)
        if organization is None:
            raise Http404("Tenant required.")

        if self.require_membership and not request.user.is_superuser:
            if get_membership(request.user, organization) is None:
                raise PermissionDenied

        if self.permission_codename:
            if not has_permission(request.user, organization, self.permission_codename):
                raise PermissionDenied

        self.organization = organization
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.setdefault("organization", getattr(self, "organization", None))
        return super().get_context_data(**kwargs)

