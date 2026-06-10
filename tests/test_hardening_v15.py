"""Tests del hardening v0.15: MFA, correlación de requests, GDPR y arnés MCP."""

from __future__ import annotations

import importlib.util
import json
import sys
import uuid
from pathlib import Path

import pytest
from django.core.management import call_command
from django.db import connection
from django.urls import reverse

from core.models import Membership, Role, User
from core.services.seed import seed_default_roles
from multitenant.models import Domain, Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, create_schema, schema_context

ROOT = Path(__file__).resolve().parents[1]


# ── MFA (allauth.mfa) ────────────────────────────────────────────────────


@pytest.mark.django_db
def test_mfa_urls_mounted_and_protected(client):
    """El módulo 2FA está montado y exige sesión (redirige a login)."""
    url = reverse("mfa_index")
    assert url == "/accounts/2fa/"
    res = client.get(url)
    assert res.status_code == 302
    assert "/accounts/login/" in res["Location"]


# ── Correlación de requests (request_id + tenant en logs) ───────────────


@pytest.mark.django_db
def test_response_carries_request_id(client):
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.headers.get("X-Request-ID")


@pytest.mark.django_db
def test_request_id_passthrough_from_proxy(client):
    res = client.get("/healthz", HTTP_X_REQUEST_ID="abc-123-proxy")
    assert res.headers.get("X-Request-ID") == "abc-123-proxy"


def test_logging_filter_defaults_outside_request():
    import logging

    from common.request_context import RequestContextFilter

    record = logging.LogRecord("x", logging.INFO, __file__, 1, "msg", None, None)
    assert RequestContextFilter().filter(record) is True
    assert record.request_id == "-"
    assert record.tenant == "-"


# ── GDPR: export y anonimización cross-schema ────────────────────────────


def _tenant_with_user(prefix: str, email: str) -> tuple[Tenant, User]:
    slug = f"{prefix}-{uuid.uuid4().hex[:8]}"
    with schema_context(PUBLIC_SCHEMA_NAME):
        tenant_public = Tenant.objects.create(name=prefix, slug=slug, schema_name=slug)
        create_schema(slug)
        Domain.objects.create(tenant=tenant_public, domain=f"{slug}.testserver", is_primary=True)
    with schema_context(slug):
        tenant_local, _ = Tenant.objects.get_or_create(
            id=tenant_public.id,
            defaults={"name": prefix, "slug": slug, "schema_name": slug},
        )
        seed_default_roles(tenant_local)
        user = User.objects.create_user(
            username=f"gdpr-{uuid.uuid4().hex[:6]}", email=email, password="Str0ngPass!123"
        )
        role = Role.objects.get(organization=tenant_local, slug="member")
        Membership.objects.create(user=user, organization=tenant_local, role=role, is_active=True)
    return tenant_public, user


@pytest.mark.django_db(transaction=True)
def test_export_user_data_collects_across_schemas(tmp_path, capsys):
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    email = f"gdpr-{uuid.uuid4().hex[:8]}@example.com"
    tenant_public, _ = _tenant_with_user("gdprexp", email)

    out_file = tmp_path / "export.json"
    call_command("export_user_data", "--email", email, "--output", str(out_file))

    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["email"] == email
    assert tenant_public.schema_name in data["schemas"]
    schema_data = data["schemas"][tenant_public.schema_name]
    assert schema_data["user"]["email"] == email
    assert len(schema_data["memberships"]) == 1


@pytest.mark.django_db(transaction=True)
def test_delete_user_data_anonymizes_everywhere(capsys):
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    email = f"gdpr-{uuid.uuid4().hex[:8]}@example.com"
    tenant_public, user = _tenant_with_user("gdprdel", email)

    call_command("delete_user_data", "--email", email, "--yes")

    with schema_context(tenant_public.schema_name):
        refreshed = User.objects.get(pk=user.pk)
        assert refreshed.email.startswith("deleted-")
        assert refreshed.email.endswith("@anonimo.invalid")
        assert refreshed.is_active is False
        assert not refreshed.has_usable_password()
        assert User.objects.filter(email__iexact=email).count() == 0
        assert Membership.objects.filter(user=refreshed, is_active=True).count() == 0


@pytest.mark.django_db(transaction=True)
def test_gdpr_commands_fail_for_unknown_email():
    from django.core.management.base import CommandError

    with pytest.raises(CommandError):
        call_command("export_user_data", "--email", "nadie@inexistente.invalid")
    with pytest.raises(CommandError):
        call_command("delete_user_data", "--email", "nadie@inexistente.invalid", "--yes")


# ── Emails async (Celery eager en tests) ─────────────────────────────────


@pytest.mark.django_db(transaction=True)
def test_welcome_email_goes_through_celery_task():
    from django.core import mail

    user = User.objects.create_user(
        username="celery-user", email="celery@example.com", password="Str0ngPass!123"
    )
    from core.services.email import EmailService

    EmailService.send_welcome_email(user)
    assert len(mail.outbox) == 1
    assert "Proyecto Semilla" in mail.outbox[0].subject


# ── Arnés MCP: el servidor expone los verbos del proyecto ───────────────


def _load_seed_server():
    spec = importlib.util.spec_from_file_location(
        "seed_server", ROOT / "scripts" / "mcp" / "seed_server.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["seed_server"] = module
    spec.loader.exec_module(module)
    return module


def test_mcp_server_registers_expected_tools():
    import asyncio

    server = _load_seed_server()
    tools = {t.name for t in asyncio.run(server.mcp.list_tools())}
    assert {
        "project_status",
        "run_lint",
        "run_typecheck",
        "run_backend_tests",
        "run_frontend_tests",
        "list_skills",
        "read_skill",
        "read_doc",
    } <= tools


def test_mcp_skills_and_docs_are_readable():
    server = _load_seed_server()
    listing = server.list_skills()
    assert "scaffold-api-endpoint" in listing

    skill = server.read_skill("scaffold-api-endpoint")
    assert "ViewSet" in skill or "viewset" in skill.lower()

    doc = server.read_doc("arnes-ia.md")
    assert "agnóstico" in doc

    # Path traversal bloqueado
    assert "❌" in server.read_skill("../../etc/passwd")
    assert "❌" in server.read_doc("../local.env")
