from __future__ import annotations

import logging
from typing import Any

from django.dispatch import receiver
from djstripe import signals
from djstripe.models import Event, Subscription as DjStripeSubscription

from billing.models import Plan, Subscription
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
    # Note: 'sender' here is the WebhookEndpoint model class, not instance usually.
    # 'event' is the processed Event object.

    event_type = event.type
    # data_object is event.data["object"], already parsed (dict).
    # dj-stripe creates model instances for supported objects.
    data_object = event.data.get("object", {})

    if event_type == "checkout.session.completed":
        _handle_checkout_completed(event, data_object)
    elif event_type in {"customer.subscription.updated", "customer.subscription.deleted"}:
        _handle_subscription_updated(event, data_object)
    elif event_type in {"invoice.payment_succeeded", "invoice.payment_failed"}:
        _handle_invoice(event, data_object)


def _handle_checkout_completed(event: Event, session_obj: dict[str, Any]) -> None:
    metadata = session_obj.get("metadata", {})
    tenant_schema = metadata.get("tenant_schema")
    tenant_id = metadata.get("tenant_id")
    plan_code = metadata.get("plan_code")

    if not tenant_schema or not tenant_id or not plan_code:
        return

    subscription_id = session_obj.get("subscription")
    if not subscription_id:
        return

    # Find tenant
    with schema_context(PUBLIC_SCHEMA_NAME):
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return

    # Fetch dj-stripe subscription instance if available
    # dj-stripe likely created it during processing if it supports it.
    dj_sub = DjStripeSubscription.objects.filter(id=subscription_id).first()

    with schema_context(tenant_schema):
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
            }
        )
        
        tenant.plan_code = plan.code
        tenant.save(update_fields=["plan_code"])
        _apply_plan_roles(tenant, plan)

def _handle_subscription_updated(event: Event, sub_obj: dict[str, Any]) -> None:
    subscription_id = sub_obj.get("id")
    status = sub_obj.get("status")
    metadata = sub_obj.get("metadata", {})
    tenant_schema = metadata.get("tenant_schema")
    tenant_id = metadata.get("tenant_id")

    if not tenant_schema:
        # Fallback: try to find our subscription by ID across tenants is hard 
        # unless we query public schema mapping or iterate.
        # Ideally we trust metadata is preserved.
        return 

    with schema_context(tenant_schema):
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return

        sub = Subscription.objects.filter(stripe_subscription_id=subscription_id, organization=tenant).first()
        if sub:
            sub.status = status
            
            # Link dj-stripe object if missing
            if not sub.djstripe_subscription:
                 sub.djstripe_subscription = DjStripeSubscription.objects.filter(id=subscription_id).first()

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
    for membership in Membership.objects.filter(organization=tenant, is_active=True).select_related("role"):
        if membership.role.slug == "owner":
            continue
        membership.role = target_role
        membership.save(update_fields=["role"])
