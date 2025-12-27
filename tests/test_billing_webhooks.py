import pytest
from unittest.mock import MagicMock, patch
from billing.webhooks import handle_event, WebhookError
from billing.models import Subscription, Invoice, Plan, Price, StripeEvent
from multitenant.schema import PUBLIC_SCHEMA_NAME, schema_context
from multitenant.models import Tenant
from core.models import Role, Membership, User
import uuid
from django.utils import timezone

@pytest.mark.django_db(transaction=True)
class TestBillingWebhooks:

    @pytest.fixture
    def tenant(self):
        slug = f"testorg-{uuid.uuid4().hex[:8]}"
        with schema_context(PUBLIC_SCHEMA_NAME):
            tenant = Tenant.objects.create(name="Test Org", slug=slug, schema_name=slug)
        
        # Ensure tenant exists in its own schema (handled by signal usually, but manual here for isolation)
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
            # Create roles needed
            Role.objects.create(organization=tenant, slug="owner", name="Owner")
            Role.objects.create(organization=tenant, slug="manager", name="Manager")
            return plan

    @pytest.fixture
    def price(self, plan):
        with schema_context(plan.organization.schema_name):
            return Price.objects.create(
                plan=plan,
                stripe_price_id="price_123",
                amount=1000,
                currency="usd"
            )

    def test_handle_event_idempotency(self):
        """Test that duplicate events are ignored."""
        event_id = "evt_test_idempotency"
        payload = {"id": event_id, "type": "checkout.session.completed"}
        
        with schema_context(PUBLIC_SCHEMA_NAME):
            StripeEvent.objects.create(event_id=event_id, event_type="checkout.session.completed", payload=payload)
        
        # Handling again should not raise error and likely do nothing
        handle_event(payload)
        
        with schema_context(PUBLIC_SCHEMA_NAME):
            assert StripeEvent.objects.filter(event_id=event_id).count() == 1

    def test_handle_event_creates_stripe_event(self):
        """Test that new events are recorded in public schema."""
        event_id = "evt_new_unique"
        payload = {"id": event_id, "type": "ping"}
        
        handle_event(payload)
        
        with schema_context(PUBLIC_SCHEMA_NAME):
            assert StripeEvent.objects.filter(event_id=event_id).exists()

    def test_handle_checkout_completed(self, tenant, plan):
        """Test processing of checkout.session.completed."""
        event_id = "evt_checkout"
        subscription_id = "sub_new"
        customer_id = "cus_new"
        
        payload = {
            "id": event_id,
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "subscription": subscription_id,
                    "customer": customer_id,
                    "metadata": {
                        "tenant_schema": tenant.schema_name,
                        "tenant_id": str(tenant.id),
                        "plan_code": plan.code
                    }
                }
            }
        }
        
        handle_event(payload)
        
        with schema_context(tenant.schema_name):
            sub = Subscription.objects.get(stripe_subscription_id=subscription_id)
            assert sub.plan == plan
            assert sub.stripe_customer_id == customer_id
            assert sub.status == "active"
            
            tenant.refresh_from_db()
            assert tenant.plan_code == plan.code

    def test_handle_subscription_updated(self, tenant, plan, price):
        """Test processing of customer.subscription.updated."""
        event_id = "evt_sub_update"
        subscription_id = "sub_existing"
        
        # Pre-create subscription
        with schema_context(tenant.schema_name):
            sub = Subscription.objects.create(
                organization=tenant,
                plan=plan,
                stripe_subscription_id=subscription_id,
                status="incomplete"
            )
        
        payload = {
            "id": event_id,
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "id": subscription_id,
                    "status": "active",
                    "currency": "usd",
                    "metadata": {
                        "tenant_schema": tenant.schema_name,
                        "tenant_id": str(tenant.id)
                    },
                    "items": {
                        "data": [{
                            "price": {"id": price.stripe_price_id},
                            "quantity": 2
                        }]
                    }
                }
            }
        }
        
        handle_event(payload)
        
        with schema_context(tenant.schema_name):
            sub.refresh_from_db()
            assert sub.status == "active"
            assert sub.quantity == 2

    def test_handle_invoice(self, tenant):
        """Test processing of invoice.payment_succeeded."""
        event_id = "evt_invoice"
        invoice_id = "in_123"
        
        payload = {
            "id": event_id,
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": invoice_id,
                    "status": "paid",
                    "amount_paid": 2000,
                    "currency": "usd",
                     "metadata": {
                        "tenant_schema": tenant.schema_name,
                        "tenant_id": str(tenant.id)
                    },
                    "created": int(timezone.now().timestamp())
                }
            }
        }
        
        handle_event(payload)
        
        with schema_context(tenant.schema_name):
            inv = Invoice.objects.get(stripe_invoice_id=invoice_id)
            assert inv.status == "paid"
            assert inv.amount_paid == 20.0  # 2000 cents
