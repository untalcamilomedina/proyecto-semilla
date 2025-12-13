from __future__ import annotations

from django.views.generic import TemplateView

from billing.models import Invoice, Plan, Subscription
from core.views.mixins import TenantPermissionMixin


class BillingDashboardView(TenantPermissionMixin, TemplateView):
    template_name = "billing/dashboard.html"
    permission_codename = "billing.manage_billing"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["plans"] = Plan.objects.filter(organization=self.organization, is_active=True)
        ctx["subscription"] = (
            Subscription.objects.filter(organization=self.organization)
            .select_related("plan")
            .order_by("-created_at")
            .first()
        )
        ctx["invoices"] = Invoice.objects.filter(organization=self.organization)[:10]
        return ctx

