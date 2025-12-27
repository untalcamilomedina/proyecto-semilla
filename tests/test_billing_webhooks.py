import pytest
from unittest.mock import MagicMock
from djstripe import signals
from djstripe.models import Event, Subscription as DjStripeSubscription
from billing.webhooks import handle_stripe_event
from billing.models import Subscription, Plan, Price
from multitenant.schema import PUBLIC_SCHEMA_NAME, schema_context
from multitenant.models import Tenant, Domain
from core.models import Role
import uuid
from django.utils import timezone
from datetime import datetime

@pytest.mark.django_db(transaction=True)
class TestBillingWebhooksDjStripe:

    @pytest.fixture
    def tenant(self):
        slug = f"testorg-{uuid.uuid4().hex[:8]}"
        with schema_context(PUBLIC_SCHEMA_NAME):
            tenant = Tenant.objects.create(name="Test Org", slug=slug, schema_name=slug)
        
        with schema_context(slug):
             Tenant.objects.get_or_create(id=tenant.id, defaults={
                 "name": tenant.name, "slug": tenant.slug, "schema_name": tenant.schema_name
             })
        return tenant

    @pytest.fixture
    def plan(self, tenant):
        with schema_context(tenant.schema_name):
            plan = Plan.objects.create(
                organization=tenant,
                name="Pro Plan",
                code="pro",
                roles_on_activation=["manager"]
            )
            Role.objects.create(organization=tenant, slug="owner", name="Owner")
            Role.objects.create(organization=tenant, slug="manager", name="Manager")
            return plan

    def test_handle_checkout_session_completed(self, tenant, plan):
        """Test reaction to checkout.session.completed via signal."""
        event_id = "evt_checkout_signal"
        subscription_id = "sub_new_signal"
        customer_id = "cus_new_signal"
        
        # Mock the Event object passed by logic
        event_mock = MagicMock(spec=Event)
        event_mock.id = event_id
        event_mock.type = "checkout.session.completed"
        event_mock.data = {
            "object": {
                "id": "cs_test_123",
                "subscription": subscription_id,
                "customer": customer_id,
                "metadata": {
                    "tenant_schema": tenant.schema_name,
                    "tenant_id": str(tenant.id),
                    "plan_code": plan.code
                }
            }
        }
        
        # Manually trigger handler or emit signal? 
        # Calling handler directly is cleaner for unit test logic.
        handle_stripe_event(sender=None, event=event_mock)
        
        with schema_context(tenant.schema_name):
            sub = Subscription.objects.filter(stripe_subscription_id=subscription_id).first()
            assert sub is not None
            assert sub.plan == plan
            assert sub.status == "active"
            
            tenant.refresh_from_db()
            assert tenant.plan_code == plan.code

    def test_handle_subscription_updated(self, tenant, plan):
        """Test reaction to customer.subscription.updated."""
        subscription_id = "sub_existing_signal"
        
        with schema_context(tenant.schema_name):
            sub = Subscription.objects.create(
                organization=tenant,
                plan=plan,
                stripe_subscription_id=subscription_id,
                status="incomplete"
            )
        
        event_mock = MagicMock(spec=Event)
        event_mock.type = "customer.subscription.updated"
        event_mock.data = {
            "object": {
                "id": subscription_id,
                "status": "active",
                "metadata": {
                    "tenant_schema": tenant.schema_name,
                    "tenant_id": str(tenant.id)
                },
                 "items": {"data": []}
            }
        }
        
        handle_stripe_event(sender=None, event=event_mock)
        
        with schema_context(tenant.schema_name):
            sub.refresh_from_db()
            assert sub.status == "active"

