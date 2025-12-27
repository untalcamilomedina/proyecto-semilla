from __future__ import annotations

from datetime import datetime
from datetime import timezone as dt_timezone
from typing import Any, Mapping

from django.conf import settings
from django.utils import timezone

from billing.models import Invoice, Plan, Price, StripeEvent, Subscription
from core.models import Membership, Role
from multitenant.models import Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, schema_context


class WebhookError(Exception):
    pass


def _stripe():
    try:
        import stripe  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise WebhookError("stripe package not installed") from exc
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def construct_event(payload: bytes, sig_header: str | None):
    stripe = _stripe()
    if not sig_header:
        raise WebhookError("Missing Stripe signature header.")
    return stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)


def handle_event(event: Mapping[str, Any]) -> None:
    event_id = event.get("id")
    event_type = event.get("type", "")

    # Idempotency in public schema
    with schema_context(PUBLIC_SCHEMA_NAME):
        if StripeEvent.objects.filter(event_id=event_id).exists():
            return
        StripeEvent.objects.create(event_id=event_id, event_type=event_type, payload=event)

    data_object = event.get("data", {}).get("object", {})
    metadata = _get_metadata(data_object)
    tenant_schema = metadata.get("tenant_schema")
    tenant_id = metadata.get("tenant_id")
    if not tenant_schema or not tenant_id:
        return

    with schema_context(tenant_schema):
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return

        if event_type == "checkout.session.completed":
            _handle_checkout_completed(tenant, data_object)
        elif event_type in {"customer.subscription.updated", "customer.subscription.deleted"}:
            _handle_subscription_updated(tenant, data_object)
        elif event_type in {"invoice.payment_succeeded", "invoice.payment_failed"}:
            _handle_invoice(tenant, data_object)


def _get_metadata(obj: Mapping[str, Any]) -> dict[str, str]:
    md = obj.get("metadata") or {}
    return {str(k): str(v) for k, v in md.items()}


def _epoch_to_dt(epoch: int | None) -> datetime | None:
    if not epoch:
        return None
    return datetime.fromtimestamp(epoch, tz=dt_timezone.utc)


def _handle_checkout_completed(tenant: Tenant, session_obj: Mapping[str, Any]) -> None:
    metadata = _get_metadata(session_obj)
    plan_code = metadata.get("plan_code")
    subscription_id = session_obj.get("subscription")
    customer_id = session_obj.get("customer")

    if not plan_code or not subscription_id:
        return

    plan = Plan.objects.filter(organization=tenant, code=plan_code).first()
    if not plan:
        return

    sub, _ = Subscription.objects.update_or_create(
        organization=tenant,
        stripe_subscription_id=subscription_id,
        defaults={
            "plan": plan,
            "stripe_customer_id": customer_id or "",
            "status": "active",
        },
    )
    tenant.plan_code = plan.code
    tenant.save(update_fields=["plan_code"])
    _apply_plan_roles(tenant, plan)


def _handle_subscription_updated(tenant: Tenant, sub_obj: Mapping[str, Any]) -> None:
    subscription_id = sub_obj.get("id")
    customer_id = sub_obj.get("customer") or ""
    status = sub_obj.get("status") or "incomplete"
    cancel_at_period_end = bool(sub_obj.get("cancel_at_period_end"))
    current_period_end = _epoch_to_dt(sub_obj.get("current_period_end"))
    trial_end = _epoch_to_dt(sub_obj.get("trial_end"))

    items = (sub_obj.get("items") or {}).get("data") or []
    price_id = None
    quantity = 1
    if items:
        item0 = items[0]
        price_id = (item0.get("price") or {}).get("id")
        quantity = item0.get("quantity") or 1

    price = Price.objects.filter(stripe_price_id=price_id, plan__organization=tenant).first()
    if not price:
        return
    plan = price.plan

    Subscription.objects.update_or_create(
        organization=tenant,
        stripe_subscription_id=subscription_id,
        defaults={
            "plan": plan,
            "stripe_customer_id": customer_id,
            "status": status,
            "quantity": quantity,
            "cancel_at_period_end": cancel_at_period_end,
            "current_period_end": current_period_end,
            "trial_end": trial_end,
        },
    )

    tenant.plan_code = plan.code
    tenant.trial_ends_at = trial_end
    tenant.save(update_fields=["plan_code", "trial_ends_at"])
    if status in {"active", "trialing"}:
        _apply_plan_roles(tenant, plan)


def _handle_invoice(tenant: Tenant, invoice_obj: Mapping[str, Any]) -> None:
    invoice_id = invoice_obj.get("id")
    if not invoice_id:
        return
    amount_paid = (invoice_obj.get("amount_paid") or 0) / 100
    currency = invoice_obj.get("currency") or settings.STRIPE_DEFAULT_CURRENCY
    status = invoice_obj.get("status") or ""
    hosted_invoice_url = invoice_obj.get("hosted_invoice_url") or ""
    invoice_pdf = invoice_obj.get("invoice_pdf") or ""
    created = _epoch_to_dt(invoice_obj.get("created")) or timezone.now()

    Invoice.objects.update_or_create(
        stripe_invoice_id=invoice_id,
        defaults={
            "organization": tenant,
            "status": status,
            "amount_paid": amount_paid,
            "currency": currency,
            "hosted_invoice_url": hosted_invoice_url,
            "invoice_pdf": invoice_pdf,
            "created_at": created,
        },
    )


def _apply_plan_roles(tenant: Tenant, plan: Plan) -> None:
    slugs = plan.roles_on_activation or []
    if not slugs:
        return
    roles = {r.slug: r for r in Role.objects.filter(organization=tenant, slug__in=slugs)}
    if not roles:
        return

    # Minimal V1 behavior: ensure owner membership has at least the first plan role.
    target_role = roles[slugs[0]]
    for membership in Membership.objects.filter(organization=tenant, is_active=True).select_related("role"):
        if membership.role.slug == "owner":
            continue
        membership.role = target_role
        membership.save(update_fields=["role"])

