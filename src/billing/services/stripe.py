from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.conf import settings

from billing.models import Plan, Price, Subscription


class StripeError(Exception):
    pass


def _stripe() -> Any:
    try:
        import stripe  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise StripeError("stripe package not installed") from exc
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


@dataclass
class CheckoutSessionResult:
    session_id: str
    url: str


def create_checkout_session(
    *,
    organization,
    price: Price,
    success_url: str,
    cancel_url: str,
    quantity: int = 1,
) -> CheckoutSessionResult:
    stripe = _stripe()
    plan: Plan = price.plan

    if not settings.STRIPE_SECRET_KEY:
        raise StripeError("STRIPE_SECRET_KEY missing.")

    metadata = {
        "tenant_id": str(organization.id),
        "tenant_schema": organization.schema_name,
        "plan_code": plan.code,
        "price_id": str(price.id),
    }

    subscription_data: dict[str, Any] = {"metadata": metadata}
    if plan.trial_days:
        subscription_data["trial_period_days"] = plan.trial_days

    session = stripe.checkout.Session.create(
        mode="subscription",
        allow_promotion_codes=True,
        line_items=[
            {
                "price": price.stripe_price_id,
                "quantity": quantity,
            }
        ],
        success_url=success_url,
        cancel_url=cancel_url,
        subscription_data=subscription_data,
        metadata=metadata,
        client_reference_id=str(organization.id),
    )

    return CheckoutSessionResult(session_id=session.id, url=session.url)


def create_billing_portal_session(*, organization, return_url: str) -> str:
    stripe = _stripe()

    subscription = (
        Subscription.objects.filter(organization=organization, stripe_customer_id__gt="")
        .order_by("-created_at")
        .first()
    )
    if not subscription or not subscription.stripe_customer_id:
        raise StripeError("No Stripe customer for organization.")

    portal = stripe.billing_portal.Session.create(
        customer=subscription.stripe_customer_id, return_url=return_url
    )
    return portal.url

