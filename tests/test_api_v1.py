import pytest
import uuid

from django.db import connection
from rest_framework.test import APIClient

from api.models import ApiKey
from core.models import Membership, Role, User
from core.services.seed import seed_default_roles
from multitenant.models import Domain, Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, create_schema, schema_context


@pytest.mark.django_db(transaction=True)
def test_api_key_auth_can_access_tenant_endpoint():
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    with schema_context(PUBLIC_SCHEMA_NAME):
        slug = f"orgapi-{uuid.uuid4().hex[:8]}"
        tenant_public = Tenant.objects.create(name="Org API", slug=slug, schema_name=slug)
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
            username="apiadmin", email="apiadmin@example.com", password="pass1234"
        )
        Membership.objects.create(user=user, organization=tenant_local, role=owner_role)
        _key, plain = ApiKey.generate(organization=tenant_local, user=user, name="default")

    client = APIClient()
    res = client.get(
        "/api/v1/tenant/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["slug"] == slug


@pytest.mark.django_db(transaction=True)
def test_roles_endpoint_requires_manage_roles_permission():
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    with schema_context(PUBLIC_SCHEMA_NAME):
        slug = f"orgapi2-{uuid.uuid4().hex[:8]}"
        tenant_public = Tenant.objects.create(name="Org API2", slug=slug, schema_name=slug)
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
        viewer_role = Role.objects.get(organization=tenant_local, slug="viewer")
        owner_role = Role.objects.get(organization=tenant_local, slug="owner")
        user = User.objects.create_user(
            username="viewer", email="viewer@example.com", password="pass1234"
        )
        membership = Membership.objects.create(
            user=user, organization=tenant_local, role=viewer_role
        )
        _key, plain = ApiKey.generate(organization=tenant_local, user=user, name="viewer")

    client = APIClient()
    payload = {"name": "Test Role", "description": "", "position": 1, "permissions": []}

    res = client.post(
        "/api/v1/roles/",
        payload,
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 403

    with schema_context(slug):
        membership.role = owner_role
        membership.save(update_fields=["role"])

    res = client.post(
        "/api/v1/roles/",
        payload,
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 201

