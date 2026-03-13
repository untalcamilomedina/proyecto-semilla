"""Billing URL configuration.

All Stripe webhook handling is via djstripe at /stripe/webhook/.
Billing data is consumed via the DRF API endpoints.
"""

from __future__ import annotations

from django.urls import path

app_name = "billing"

urlpatterns: list = []
