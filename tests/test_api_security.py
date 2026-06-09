"""Tests de seguridad transversales del API.

Cubren los invariantes que el boilerplate garantiza:
1. Ningún endpoint de tenant responde a usuarios anónimos.
2. Un usuario autenticado de un tenant NO accede a datos de otro tenant
   (membresía obligatoria — deny by default).
3. Un JWT emitido en un schema no autentica en otro (binding por claim).
4. Los permisos por codename se aplican (viewer no ve billing).
5. /metrics queda cerrado fuera de DEBUG sin token.
"""

from __future__ import annotations

import uuid

import pytest
from django.db import connection
from rest_framework.test import APIClient

from core.models import Membership, Role, User
from core.services.seed import seed_default_roles
from multitenant.models import Domain, Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, create_schema, schema_context

SENSITIVE_GET_ENDPOINTS = [
    "/api/v1/me/",
    "/api/v1/tenant/",
    "/api/v1/dashboard/",
    "/api/v1/memberships/",
    "/api/v1/roles/",
    "/api/v1/permissions/",
    "/api/v1/plans/",
    "/api/v1/subscriptions/",
    "/api/v1/invoices/",
    "/api/v1/api-keys/",
    "/api/v1/activity-logs/",
]


def _make_tenant(prefix: str) -> tuple[Tenant, str]:
    """Crea tenant público + schema + dominio. Devuelve (tenant_public, host)."""
    slug = f"{prefix}-{uuid.uuid4().hex[:8]}"
    host = f"{slug}.testserver"
    with schema_context(PUBLIC_SCHEMA_NAME):
        tenant_public = Tenant.objects.create(name=prefix, slug=slug, schema_name=slug)
        create_schema(slug)
        Domain.objects.create(tenant=tenant_public, domain=host, is_primary=True)
    return tenant_public, host


def _seed_tenant_user(tenant_public: Tenant, username: str, role_slug: str = "owner") -> User:
    """Dentro del schema del tenant: roles por defecto + usuario con membresía."""
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
@pytest.mark.parametrize("endpoint", SENSITIVE_GET_ENDPOINTS)
def test_anonymous_cannot_access_tenant_endpoints(endpoint):
    """Todos los endpoints sensibles exigen autenticación (401/403)."""
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    _, host = _make_tenant("anon")
    client = APIClient()
    res = client.get(endpoint, HTTP_HOST=host)
    assert res.status_code in (401, 403), f"{endpoint} respondió {res.status_code}"


@pytest.mark.django_db(transaction=True)
def test_anonymous_cannot_logout():
    client = APIClient()
    res = client.post("/api/v1/logout/")
    assert res.status_code in (401, 403)


@pytest.mark.django_db(transaction=True)
def test_cross_tenant_user_cannot_list_other_tenant_members():
    """Usuario del tenant A (autenticado) NO lista miembros del tenant B."""
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    tenant_a, _host_a = _make_tenant("orga")
    tenant_b, host_b = _make_tenant("orgb")

    user_a = _seed_tenant_user(tenant_a, "alice")
    # El tenant B tiene su propio usuario y membresía (datos que NO debe ver A).
    _seed_tenant_user(tenant_b, "bob")

    client = APIClient()
    client.force_authenticate(user=user_a)
    res = client.get("/api/v1/memberships/", HTTP_HOST=host_b)
    assert res.status_code == 403, (
        f"Fuga cross-tenant: usuario de {tenant_a.slug} obtuvo "
        f"{res.status_code} en {tenant_b.slug}"
    )


@pytest.mark.django_db(transaction=True)
def test_jwt_minted_in_one_schema_rejected_in_another():
    """El claim schema_name ata el token a su schema de origen."""
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    from api.serializers_auth import TenantTokenObtainPairSerializer

    tenant_a, host_a = _make_tenant("jwta")
    tenant_b, host_b = _make_tenant("jwtb")

    user_a = _seed_tenant_user(tenant_a, "alice-jwt")
    _seed_tenant_user(tenant_b, "bob-jwt")

    with schema_context(tenant_a.schema_name):
        token = TenantTokenObtainPairSerializer.get_token(user_a)
        access = str(token.access_token)
        assert token["schema_name"] == tenant_a.schema_name

    client = APIClient()
    # En su propio tenant el token funciona.
    res_own = client.get("/api/v1/me/", HTTP_HOST=host_a, HTTP_AUTHORIZATION=f"Bearer {access}")
    assert res_own.status_code == 200

    # En otro tenant, el mismo token debe rechazarse (los IDs de usuario
    # colisionan entre schemas: sin binding habría suplantación).
    res_other = client.get("/api/v1/me/", HTTP_HOST=host_b, HTTP_AUTHORIZATION=f"Bearer {access}")
    assert res_other.status_code == 401


@pytest.mark.django_db(transaction=True)
def test_viewer_cannot_read_billing():
    """billing.manage_billing se exige en subscriptions/invoices."""
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    tenant, host = _make_tenant("bill")
    viewer = _seed_tenant_user(tenant, "viewer-user", role_slug="viewer")

    client = APIClient()
    client.force_authenticate(user=viewer)
    for endpoint in ("/api/v1/subscriptions/", "/api/v1/invoices/"):
        res = client.get(endpoint, HTTP_HOST=host)
        assert res.status_code == 403, f"{endpoint} devolvió {res.status_code}"


@pytest.mark.django_db
def test_metrics_requires_token_outside_debug(settings, client):
    settings.DEBUG = False
    settings.METRICS_TOKEN = ""
    assert client.get("/metrics").status_code == 403

    settings.METRICS_TOKEN = "s3cret-metrics"
    assert client.get("/metrics").status_code == 403
    res = client.get("/metrics", HTTP_AUTHORIZATION="Bearer s3cret-metrics")
    assert res.status_code == 200


@pytest.mark.django_db
def test_signup_enforces_password_validators():
    """El signup aplica AUTH_PASSWORD_VALIDATORS (no solo longitud 8)."""
    client = APIClient()
    res = client.post(
        "/api/v1/signup/",
        {"email": "weak@example.com", "password1": "12345678", "password2": "12345678"},
        format="json",
    )
    assert res.status_code == 400
    assert "password1" in res.data
