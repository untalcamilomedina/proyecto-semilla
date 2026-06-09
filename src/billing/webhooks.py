from __future__ import annotations

import logging
from typing import Any

from django.dispatch import receiver
from djstripe import signals
from djstripe.models import Event
from djstripe.models import Subscription as DjStripeSubscription

from billing.models import Plan, StripeEvent, Subscription
from core.models import Membership, Role
from multitenant.models import Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, schema_context

logger = logging.getLogger(__name__)

# We listen to specific events or the generic one. dj-stripe often relies on specific signals,
# but webhook_event_processed is a safe catch-all if we check event type.


@receiver(signals.webhook_processing_error)
def handle_webhook_error(sender, exception: Exception, data: dict, **kwargs) -> None:
    logger.error(f"Webhook processing error: {exception}", extra={"data": data})


@receiver(signals.webhook_post_process)
def handle_stripe_event(sender, event: Event, **kwargs: Any) -> None:
    """
    Central handler for processed Stripe events.
    Dispatches to specific logic based on event.type.
    """
    event_type = event.type
    data_object = event.data.get("object", {})

    # Idempotencia: si ya procesamos este event_id, no repetir efectos.
    with schema_context(PUBLIC_SCHEMA_NAME):
        _, created = StripeEvent.objects.get_or_create(
            event_id=event.id,
            defaults={"event_type": event_type, "payload": event.data},
        )
    if not created:
        logger.info("Stripe event %s already processed; skipping.", event.id)
        return

    if event_type == "checkout.session.completed":
        _handle_checkout_completed(event, data_object)
    elif event_type in {"customer.subscription.updated", "customer.subscription.deleted"}:
        _handle_subscription_updated(event, data_object)
    elif event_type in {"invoice.payment_succeeded", "invoice.payment_failed"}:
        _handle_invoice(event, data_object)


def _resolve_tenant(metadata: dict[str, Any]) -> Tenant | None:
    """Resuelve y VALIDA el tenant indicado en la metadata del evento.

    Nunca usamos `tenant_schema` del payload directamente: se busca el tenant
    por id en el schema público y se verifica que su schema_name coincida.
    """
    tenant_id = metadata.get("tenant_id")
    tenant_schema = metadata.get("tenant_schema")
    try:
        tenant_id = int(tenant_id)
    except (TypeError, ValueError):
        logger.warning("Stripe metadata con tenant_id inválido: %r", tenant_id)
        return None

    with schema_context(PUBLIC_SCHEMA_NAME):
        tenant = Tenant.objects.filter(id=tenant_id, is_active=True).first()

    if tenant is None:
        logger.warning("Stripe metadata apunta a tenant inexistente: %s", tenant_id)
        return None
    if tenant_schema and tenant.schema_name != tenant_schema:
        logger.warning(
            "Stripe metadata inconsistente: tenant %s tiene schema %s, metadata dice %s",
            tenant_id,
            tenant.schema_name,
            tenant_schema,
        )
        return None
    return tenant


def _handle_checkout_completed(event: Event, session_obj: dict[str, Any]) -> None:
    metadata = session_obj.get("metadata", {})
    plan_code = metadata.get("plan_code")
    if not plan_code:
        return

    tenant = _resolve_tenant(metadata)
    if tenant is None:
        return

    subscription_id = session_obj.get("subscription")
    if not subscription_id:
        return

    # Fetch dj-stripe subscription instance if available
    dj_sub = DjStripeSubscription.objects.filter(id=subscription_id).first()

    with schema_context(tenant.schema_name):
        plan = Plan.objects.filter(code=plan_code).first()
        if not plan:
            return

        Subscription.objects.update_or_create(
            organization=tenant,
            stripe_subscription_id=subscription_id,
            defaults={
                "plan": plan,
                "status": "active",
                "stripe_customer_id": session_obj.get("customer"),
                "djstripe_subscription": dj_sub,
            },
        )

        tenant.plan_code = plan.code
        tenant.save(update_fields=["plan_code"])
        _apply_plan_roles(tenant, plan)


def _handle_subscription_updated(event: Event, sub_obj: dict[str, Any]) -> None:
    subscription_id = sub_obj.get("id")
    status = sub_obj.get("status")
    valid_statuses = {choice for choice, _ in Subscription.STATUS_CHOICES}
    if status not in valid_statuses:
        logger.warning("Stripe subscription status desconocido: %r", status)
        return

    tenant = _resolve_tenant(sub_obj.get("metadata", {}))
    if tenant is None:
        return

    with schema_context(tenant.schema_name):
        sub = Subscription.objects.filter(
            stripe_subscription_id=subscription_id, organization=tenant
        ).first()
        if sub:
            sub.status = status

            # Link dj-stripe object if missing
            if not sub.djstripe_subscription:
                sub.djstripe_subscription = DjStripeSubscription.objects.filter(
                    id=subscription_id
                ).first()

            sub.save(update_fields=["status", "djstripe_subscription"])

            if status == "active" and sub.plan:
                _apply_plan_roles(tenant, sub.plan)


def _handle_invoice(event: Event, invoice_obj: dict[str, Any]) -> None:
    # We might implement invoice tracking later via dj-stripe models directly
    pass


def _apply_plan_roles(tenant: Tenant, plan: Plan) -> None:
    slugs = plan.roles_on_activation or []
    if not slugs:
        return
    roles = {r.slug: r for r in Role.objects.filter(organization=tenant, slug__in=slugs)}
    if not roles:
        return

    target_role = roles[slugs[0]]
    for membership in Membership.objects.filter(organization=tenant, is_active=True).select_related(
        "role"
    ):
        if membership.role.slug == "owner":
            continue
        membership.role = target_role
        membership.save(update_fields=["role"])
