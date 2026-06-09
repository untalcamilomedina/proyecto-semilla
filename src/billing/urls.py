"""Billing URL configuration.

All Stripe webhook handling is via djstripe at /stripe/webhook/.
Billing data is consumed via the DRF API endpoints.
"""

from __future__ import annotations

app_name = "billing"

urlpatterns: list = []
