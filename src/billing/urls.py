from __future__ import annotations

from django.urls import path

from .views import stripe_webhook
from .views_dashboard import BillingDashboardView

app_name = "billing"

urlpatterns = [
    path("", BillingDashboardView.as_view(), name="dashboard"),
    path("webhooks/stripe/", stripe_webhook, name="stripe_webhook"),
]
