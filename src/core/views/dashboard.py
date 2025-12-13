from __future__ import annotations

from django.views.generic import TemplateView

from .mixins import TenantPermissionMixin


class DashboardView(TenantPermissionMixin, TemplateView):
    template_name = "core/dashboard.html"
    require_membership = True

