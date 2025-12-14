import pytest
import uuid

from django.db import connection

from billing.models import Plan, Price, StripeEvent, Subscription
from billing.services.seed import seed_demo_plans
from billing.webhooks import handle_event
from multitenant.models import Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, create_schema, schema_context


@pytest.mark.django_db(transaction=True)
def test_seed_demo_plans_creates_plans_and_prices():
    with schema_context(PUBLIC_SCHEMA_NAME):
        slug = f"orgbill-{uuid.uuid4().hex[:8]}"
        tenant_public = Tenant.objects.create(
            name="Org Billing", slug=slug, schema_name=slug
        )
        create_schema(slug)

    with schema_context(slug):
        tenant_local, _ = Tenant.objects.get_or_create(
            id=tenant_public.id,
            defaults={
                "name": tenant_public.name,
                "slug": tenant_public.slug,
                "schema_name": tenant_public.schema_name,
            }
        )
        plans = seed_demo_plans(tenant_local)
        assert {p.code for p in plans} == {"free", "pro", "business"}
        assert Price.objects.filter(plan__organization=tenant_local).count() == 3


@pytest.mark.django_db(transaction=True)
def test_handle_event_checkout_completed_idempotent():
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    with schema_context(PUBLIC_SCHEMA_NAME):
        slug = f"orgw-{uuid.uuid4().hex[:8]}"
        tenant_public = Tenant.objects.create(name="Org W", slug=slug, schema_name=slug)
        create_schema(slug)

    with schema_context(slug):
        tenant_local, _ = Tenant.objects.get_or_create(
            id=tenant_public.id,
            defaults={
                "name": tenant_public.name,
                "slug": tenant_public.slug,
                "schema_name": tenant_public.schema_name,
            }
        )
        seed_demo_plans(tenant_local)

    event = {
        "id": "evt_test_1",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "subscription": "sub_test_1",
                "customer": "cus_test_1",
                "metadata": {
                    "tenant_id": str(tenant_public.id),
                    "tenant_schema": slug,
                    "plan_code": "pro",
                },
            }
        },
    }

    handle_event(event)
    handle_event(event)

    with schema_context(PUBLIC_SCHEMA_NAME):
        assert StripeEvent.objects.filter(event_id="evt_test_1").count() == 1

    with schema_context(slug):
        assert Subscription.objects.filter(stripe_subscription_id="sub_test_1").count() == 1
        tenant_local.refresh_from_db()
        assert tenant_local.plan_code == "pro"

