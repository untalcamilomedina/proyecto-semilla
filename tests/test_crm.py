"""Tests del módulo CRM (opcional, ENABLE_CRM).

Cubre los invariantes de seguridad del seed aplicados al módulo:
- anónimo → 401/403
- miembro de otro tenant → 403 (aislamiento)
- miembro sin crm.manage_crm → lee pero no escribe
- owner → CRUD completo + resumen de pipeline
"""

from __future__ import annotations

import uuid

import pytest
from django.conf import settings
from django.db import connection
from rest_framework.test import APIClient

from core.models import Membership, Role, User
from core.services.seed import seed_default_roles
from multitenant.models import Domain, Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, create_schema, schema_context

pytestmark = pytest.mark.skipif(
    "crm" not in settings.INSTALLED_APPS, reason="CRM module not enabled"
)


def _make_tenant(prefix: str) -> tuple[Tenant, str]:
    slug = f"{prefix}-{uuid.uuid4().hex[:8]}"
    host = f"{slug}.testserver"
    with schema_context(PUBLIC_SCHEMA_NAME):
        tenant_public = Tenant.objects.create(name=prefix, slug=slug, schema_name=slug)
        create_schema(slug)
        Domain.objects.create(tenant=tenant_public, domain=host, is_primary=True)
    return tenant_public, host


def _seed_tenant_user(tenant_public: Tenant, username: str, role_slug: str = "owner") -> User:
    with schema_context(tenant_public.schema_name):
        tenant_local, _ = Tenant.objects.get_or_create(
            id=tenant_public.id,
            defaults={
                "name": tenant_public.name,
                "slug": tenant_public.slug,
                "schema_name": tenant_public.schema_name,
            },
        )
        seed_default_roles(tenant_local)
        role = Role.objects.get(organization=tenant_local, slug=role_slug)
        user = User.objects.create_user(
            username=username, email=f"{username}@example.com", password="Str0ngPass!123"
        )
        Membership.objects.create(user=user, organization=tenant_local, role=role, is_active=True)
        return user


@pytest.mark.django_db(transaction=True)
def test_crm_requires_authentication():
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    _, host = _make_tenant("crmanon")
    client = APIClient()
    for endpoint in ("companies", "contacts", "deals", "activities"):
        res = client.get(f"/api/v1/crm/{endpoint}/", HTTP_HOST=host)
        assert res.status_code in (401, 403), f"{endpoint}: {res.status_code}"


@pytest.mark.django_db(transaction=True)
def test_crm_owner_full_crud_and_pipeline():
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    tenant, host = _make_tenant("crmown")
    owner = _seed_tenant_user(tenant, "crm-owner", role_slug="owner")

    client = APIClient()
    client.force_authenticate(user=owner)

    res = client.post(
        "/api/v1/crm/companies/",
        {"name": "Globex", "industry": "Manufacturing"},
        format="json",
        HTTP_HOST=host,
    )
    assert res.status_code == 201, res.data
    company_id = res.data["id"]

    res = client.post(
        "/api/v1/crm/contacts/",
        {
            "first_name": "Hank",
            "last_name": "Scorpio",
            "email": "hank@globex.test",
            "company": company_id,
            "status": "lead",
        },
        format="json",
        HTTP_HOST=host,
    )
    assert res.status_code == 201, res.data
    contact_id = res.data["id"]
    assert res.data["company_name"] == "Globex"

    res = client.post(
        "/api/v1/crm/deals/",
        {
            "name": "Plan anual",
            "company": company_id,
            "contact": contact_id,
            "amount": "1200.00",
            "stage": "qualified",
            "probability": 40,
        },
        format="json",
        HTTP_HOST=host,
    )
    assert res.status_code == 201, res.data
    deal_id = res.data["id"]

    # Cerrar el deal como ganado fija closed_at automáticamente.
    res = client.patch(
        f"/api/v1/crm/deals/{deal_id}/", {"stage": "won"}, format="json", HTTP_HOST=host
    )
    assert res.status_code == 200, res.data
    assert res.data["closed_at"] is not None

    res = client.post(
        "/api/v1/crm/activities/",
        {"kind": "call", "subject": "Kickoff", "deal": deal_id, "contact": contact_id},
        format="json",
        HTTP_HOST=host,
    )
    assert res.status_code == 201, res.data
    assert res.data["created_by_email"] == "crm-owner@example.com"

    res = client.get("/api/v1/crm/deals/pipeline/", HTTP_HOST=host)
    assert res.status_code == 200
    assert res.data["stages"]["won"]["count"] == 1
    assert res.data["stages"]["won"]["total_amount"] == "1200.00"


@pytest.mark.django_db(transaction=True)
def test_crm_member_can_read_but_not_write():
    """member no tiene crm.manage_crm: lectura sí, escritura 403."""
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    tenant, host = _make_tenant("crmro")
    member = _seed_tenant_user(tenant, "crm-member", role_slug="member")

    client = APIClient()
    client.force_authenticate(user=member)

    res = client.get("/api/v1/crm/contacts/", HTTP_HOST=host)
    assert res.status_code == 200

    res = client.post(
        "/api/v1/crm/contacts/", {"first_name": "Nope"}, format="json", HTTP_HOST=host
    )
    assert res.status_code == 403


@pytest.mark.django_db(transaction=True)
def test_crm_cross_tenant_isolation():
    """Un owner del tenant A no accede al CRM del tenant B."""
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    tenant_a, _host_a = _make_tenant("crma")
    tenant_b, host_b = _make_tenant("crmb")
    user_a = _seed_tenant_user(tenant_a, "crm-alice")
    _seed_tenant_user(tenant_b, "crm-bob")

    client = APIClient()
    client.force_authenticate(user=user_a)
    res = client.get("/api/v1/crm/contacts/", HTTP_HOST=host_b)
    assert res.status_code == 403
