import pytest
import uuid

from django.db import connection

from core.models import Membership, Role, User
from core.services.seed import seed_default_roles
from multitenant.models import Domain, Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, create_schema, schema_context


@pytest.mark.django_db(transaction=True)
def test_dashboard_and_members_views_render(client):
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    with schema_context(PUBLIC_SCHEMA_NAME):
        slug = f"orgfe-{uuid.uuid4().hex[:8]}"
        tenant_public = Tenant.objects.create(name="Org FE", slug=slug, schema_name=slug)
        create_schema(slug)
        Domain.objects.create(tenant=tenant_public, domain=f"{slug}.acme.dev", is_primary=True)

    with schema_context(slug):
        tenant_local, _ = Tenant.objects.get_or_create(
            id=tenant_public.id,
            defaults={
                "name": tenant_public.name,
                "slug": tenant_public.slug,
                "schema_name": tenant_public.schema_name,
            }
        )
        seed_default_roles(tenant_local)
        owner_role = Role.objects.get(organization=tenant_local, slug="owner")
        user = User.objects.create_user(
            username="ownerfe", email="ownerfe@example.com", password="pass1234"
        )
        Membership.objects.create(user=user, organization=tenant_local, role=owner_role)

    client.login(username="ownerfe", password="pass1234")
    res = client.get("/", HTTP_HOST=f"{slug}.acme.dev")
    assert res.status_code == 200
    res = client.get("/members/", HTTP_HOST=f"{slug}.acme.dev")
    assert res.status_code == 200

