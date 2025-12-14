import uuid
from decimal import Decimal

import pytest
from django.db import connection
from rest_framework.test import APIClient

from api.models import ApiKey
from billing.models import Invoice, Plan, Subscription
from core.models import Membership, Role, User
from core.services.seed import seed_default_roles
from multitenant.models import Domain, Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, create_schema, schema_context


@pytest.mark.django_db(transaction=True)
def test_membership_viewset_list():
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    with schema_context(PUBLIC_SCHEMA_NAME):
        slug = f"orgmem-{uuid.uuid4().hex[:8]}"
        tenant_public = Tenant.objects.create(name="Org Members", slug=slug, schema_name=slug)
        create_schema(slug)
        Domain.objects.create(tenant=tenant_public, domain=f"{slug}.acme.dev", is_primary=True)

    with schema_context(slug):
        tenant_local, _ = Tenant.objects.get_or_create(
            id=tenant_public.id,
            defaults={
                "name": tenant_public.name,
                "slug": tenant_public.slug,
                "schema_name": tenant_public.schema_name,
            },
        )
        seed_default_roles(tenant_local)
        owner_role = Role.objects.get(organization=tenant_local, slug="owner")
        user = User.objects.create_user(
            username="memadmin", email="memadmin@example.com", password="pass1234"
        )
        Membership.objects.create(user=user, organization=tenant_local, role=owner_role)
        _key, plain = ApiKey.generate(organization=tenant_local, user=user, name="default")

    client = APIClient()

    res = client.post(
        "/api/v1/memberships/invite/",
        {"emails": ["invited1@example.com"]},
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["invited"] == 1

    res = client.post(
        "/api/v1/memberships/invite/",
        {"emails": ["invited2@example.com"], "role_slug": "viewer"},
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["invited"] == 1

    res = client.get(
        "/api/v1/memberships/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["count"] == 3
    emails = {m["user_email"] for m in res.data["results"]}
    assert emails == {"memadmin@example.com", "invited1@example.com", "invited2@example.com"}
    invited2 = next(m for m in res.data["results"] if m["user_email"] == "invited2@example.com")
    assert invited2["role_slug"] == "viewer"


@pytest.mark.django_db(transaction=True)
def test_membership_viewset_update_role():
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    with schema_context(PUBLIC_SCHEMA_NAME):
        slug = f"orgmem2-{uuid.uuid4().hex[:8]}"
        tenant_public = Tenant.objects.create(name="Org Members 2", slug=slug, schema_name=slug)
        create_schema(slug)
        Domain.objects.create(tenant=tenant_public, domain=f"{slug}.acme.dev", is_primary=True)

    with schema_context(slug):
        tenant_local, _ = Tenant.objects.get_or_create(
            id=tenant_public.id,
            defaults={
                "name": tenant_public.name,
                "slug": tenant_public.slug,
                "schema_name": tenant_public.schema_name,
            },
        )
        seed_default_roles(tenant_local)
        owner_role = Role.objects.get(organization=tenant_local, slug="owner")
        user = User.objects.create_user(
            username="memadmin2", email="memadmin2@example.com", password="pass1234"
        )
        Membership.objects.create(user=user, organization=tenant_local, role=owner_role)
        member_user = User.objects.create_user(
            username="member1", email="member1@example.com", password="pass1234"
        )
        _key, plain = ApiKey.generate(organization=tenant_local, user=user, name="default")

    client = APIClient()
    res = client.post(
        "/api/v1/memberships/",
        {"user": member_user.id, "role_slug": "member"},
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 201
    membership_id = res.data["id"]
    assert res.data["user"] == member_user.id
    assert res.data["role_slug"] == "member"

    res = client.patch(
        f"/api/v1/memberships/{membership_id}/",
        {"role_slug": "viewer"},
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["role_slug"] == "viewer"
    assert res.data["role_name"] == "Viewer"

    with schema_context(slug):
        membership = Membership.objects.get(id=membership_id)
        assert membership.organization_id == tenant_public.id
        assert membership.role.slug == "viewer"


@pytest.mark.django_db(transaction=True)
def test_permission_viewset_list():
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    with schema_context(PUBLIC_SCHEMA_NAME):
        slug = f"orgperm-{uuid.uuid4().hex[:8]}"
        tenant_public = Tenant.objects.create(name="Org Perms", slug=slug, schema_name=slug)
        create_schema(slug)
        Domain.objects.create(tenant=tenant_public, domain=f"{slug}.acme.dev", is_primary=True)

    with schema_context(slug):
        tenant_local, _ = Tenant.objects.get_or_create(
            id=tenant_public.id,
            defaults={
                "name": tenant_public.name,
                "slug": tenant_public.slug,
                "schema_name": tenant_public.schema_name,
            },
        )
        seed_default_roles(tenant_local)
        owner_role = Role.objects.get(organization=tenant_local, slug="owner")
        user = User.objects.create_user(
            username="permadmin", email="permadmin@example.com", password="pass1234"
        )
        Membership.objects.create(user=user, organization=tenant_local, role=owner_role)
        _key, plain = ApiKey.generate(organization=tenant_local, user=user, name="default")

    client = APIClient()
    res = client.get(
        "/api/v1/permissions/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    codenames = {p["codename"] for p in res.data["results"]}
    assert {"core.manage_roles", "core.invite_members", "billing.manage_billing"}.issubset(codenames)

    res = client.get(
        "/api/v1/roles/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    role_slugs = {r["slug"] for r in res.data["results"]}
    assert {"owner", "admin", "editor", "member", "viewer"}.issubset(role_slugs)


@pytest.mark.django_db(transaction=True)
def test_plan_viewset_list():
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    with schema_context(PUBLIC_SCHEMA_NAME):
        slug = f"orgplan-{uuid.uuid4().hex[:8]}"
        tenant_public = Tenant.objects.create(name="Org Plans", slug=slug, schema_name=slug)
        create_schema(slug)
        Domain.objects.create(tenant=tenant_public, domain=f"{slug}.acme.dev", is_primary=True)

    with schema_context(slug):
        tenant_local, _ = Tenant.objects.get_or_create(
            id=tenant_public.id,
            defaults={
                "name": tenant_public.name,
                "slug": tenant_public.slug,
                "schema_name": tenant_public.schema_name,
            },
        )
        seed_default_roles(tenant_local)
        owner_role = Role.objects.get(organization=tenant_local, slug="owner")
        user = User.objects.create_user(
            username="planadmin", email="planadmin@example.com", password="pass1234"
        )
        Membership.objects.create(user=user, organization=tenant_local, role=owner_role)
        _key, plain = ApiKey.generate(organization=tenant_local, user=user, name="default")

        Plan.objects.create(
            organization=tenant_local,
            code="pro",
            name="Pro",
            description="",
            seat_limit=10,
            trial_days=14,
            roles_on_activation=["member"],
            is_active=True,
            is_public=True,
        )
        Plan.objects.create(
            organization=tenant_local,
            code="inactive",
            name="Inactive",
            is_active=False,
            is_public=True,
        )
        Plan.objects.create(
            organization=tenant_local,
            code="private",
            name="Private",
            is_active=True,
            is_public=False,
        )
        other_tenant = Tenant.objects.create(
            name="Other Org",
            slug=f"{slug}-other",
            schema_name=f"{slug}-other",
        )
        Plan.objects.create(
            organization=other_tenant,
            code="other",
            name="Other",
            is_active=True,
            is_public=True,
        )

    client = APIClient()
    res = client.get(
        "/api/v1/plans/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["count"] == 1
    assert res.data["results"][0]["code"] == "pro"


@pytest.mark.django_db(transaction=True)
def test_subscription_viewset_operations():
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    with schema_context(PUBLIC_SCHEMA_NAME):
        slug = f"orgsub-{uuid.uuid4().hex[:8]}"
        tenant_public = Tenant.objects.create(name="Org Subs", slug=slug, schema_name=slug)
        create_schema(slug)
        Domain.objects.create(tenant=tenant_public, domain=f"{slug}.acme.dev", is_primary=True)

    with schema_context(slug):
        tenant_local, _ = Tenant.objects.get_or_create(
            id=tenant_public.id,
            defaults={
                "name": tenant_public.name,
                "slug": tenant_public.slug,
                "schema_name": tenant_public.schema_name,
            },
        )
        seed_default_roles(tenant_local)
        owner_role = Role.objects.get(organization=tenant_local, slug="owner")
        user = User.objects.create_user(
            username="subadmin", email="subadmin@example.com", password="pass1234"
        )
        Membership.objects.create(user=user, organization=tenant_local, role=owner_role)
        _key, plain = ApiKey.generate(organization=tenant_local, user=user, name="default")

        plan = Plan.objects.create(
            organization=tenant_local,
            code="pro",
            name="Pro",
            seat_limit=10,
            trial_days=0,
            roles_on_activation=["member"],
            is_active=True,
            is_public=True,
        )
        subscription = Subscription.objects.create(
            organization=tenant_local,
            plan=plan,
            stripe_customer_id="cus_test_1",
            stripe_subscription_id="sub_test_1",
            status="active",
            quantity=2,
            cancel_at_period_end=False,
        )
        other_tenant = Tenant.objects.create(
            name="Other Org",
            slug=f"{slug}-other",
            schema_name=f"{slug}-other",
        )
        other_plan = Plan.objects.create(
            organization=other_tenant,
            code="other",
            name="Other",
            is_active=True,
            is_public=True,
        )
        Subscription.objects.create(
            organization=other_tenant,
            plan=other_plan,
            stripe_subscription_id="sub_other",
            status="active",
        )

    client = APIClient()

    res = client.get(
        "/api/v1/subscriptions/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["count"] == 1
    assert res.data["results"][0]["id"] == subscription.id
    assert res.data["results"][0]["plan"]["code"] == "pro"

    res = client.post(
        "/api/v1/subscriptions/",
        {},
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 405

    res = client.get(
        f"/api/v1/subscriptions/{subscription.id}/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 404

    res = client.get(
        "/api/v1/api-keys/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["count"] == 1

    res = client.post(
        "/api/v1/api-keys/",
        {"name": "secondary", "scopes": ["billing:read"]},
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 201
    assert res.data["name"] == "secondary"
    assert res.data["scopes"] == ["billing:read"]
    assert res.data["key"].startswith("ak_")
    key_with_scopes_id = res.data["id"]

    res = client.post(
        "/api/v1/api-keys/",
        {"name": "scopeless"},
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 201
    assert res.data["name"] == "scopeless"
    assert res.data["scopes"] == []
    assert res.data["key"].startswith("ak_")
    revoked_key_id = res.data["id"]

    res = client.get(
        "/api/v1/api-keys/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["count"] == 3
    ids = {k["id"] for k in res.data["results"]}
    assert {key_with_scopes_id, revoked_key_id}.issubset(ids)

    res = client.post(
        f"/api/v1/api-keys/{revoked_key_id}/revoke/",
        {},
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 204

    res = client.get(
        "/api/v1/api-keys/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["count"] == 2
    ids = {k["id"] for k in res.data["results"]}
    assert revoked_key_id not in ids

    with schema_context(slug):
        assert ApiKey.objects.get(id=revoked_key_id).revoked_at is not None


@pytest.mark.django_db(transaction=True)
def test_invoice_viewset_list():
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    with schema_context(PUBLIC_SCHEMA_NAME):
        slug = f"orginv-{uuid.uuid4().hex[:8]}"
        tenant_public = Tenant.objects.create(name="Org Invoices", slug=slug, schema_name=slug)
        create_schema(slug)
        Domain.objects.create(tenant=tenant_public, domain=f"{slug}.acme.dev", is_primary=True)

    with schema_context(slug):
        tenant_local, _ = Tenant.objects.get_or_create(
            id=tenant_public.id,
            defaults={
                "name": tenant_public.name,
                "slug": tenant_public.slug,
                "schema_name": tenant_public.schema_name,
            },
        )
        seed_default_roles(tenant_local)
        owner_role = Role.objects.get(organization=tenant_local, slug="owner")
        user = User.objects.create_user(
            username="invadmin", email="invadmin@example.com", password="pass1234"
        )
        Membership.objects.create(user=user, organization=tenant_local, role=owner_role)
        _key, plain = ApiKey.generate(organization=tenant_local, user=user, name="default")

        local_invoice = Invoice.objects.create(
            organization=tenant_local,
            stripe_invoice_id=f"in_{uuid.uuid4().hex}",
            status="paid",
            amount_paid=Decimal("12.34"),
            currency="usd",
            hosted_invoice_url="https://example.com/i/1",
            invoice_pdf="https://example.com/i/1.pdf",
        )
        other_tenant = Tenant.objects.create(
            name="Other Org",
            slug=f"{slug}-other",
            schema_name=f"{slug}-other",
        )
        Invoice.objects.create(
            organization=other_tenant,
            stripe_invoice_id=f"in_{uuid.uuid4().hex}",
            status="open",
            amount_paid=Decimal("0.00"),
            currency="usd",
        )

    client = APIClient()
    res = client.get(
        "/api/v1/invoices/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["count"] == 1
    assert res.data["results"][0]["id"] == local_invoice.id
    assert res.data["results"][0]["stripe_invoice_id"] == local_invoice.stripe_invoice_id

