import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import connection

from multitenant.models import Domain, Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, create_schema, get_current_schema, schema_context


@pytest.mark.django_db(transaction=True)
def test_create_tenant_command_creates_schema_and_domain():
    call_command("create_tenant", "Foo Org", "foo", domain="foo.acme.dev", no_color=True)
    tenant = Tenant.objects.get(slug="foo")
    assert Domain.objects.filter(domain="foo.acme.dev", tenant=tenant, is_primary=True).exists()

    with connection.cursor() as cursor:
        cursor.execute(
            "select schema_name from information_schema.schemata where schema_name = 'foo'"
        )
        assert cursor.fetchone() is not None


@pytest.mark.django_db
def test_reserved_subdomain_rejected():
    tenant = Tenant(name="X", slug="api", schema_name="api")
    with pytest.raises(ValidationError):
        tenant.full_clean()


@pytest.mark.django_db(transaction=True)
def test_schema_context_switches_and_restores():
    call_command("create_tenant", "Bar Org", "bar", domain="bar.acme.dev", no_color=True)

    assert get_current_schema() == PUBLIC_SCHEMA_NAME
    with schema_context("bar"):
        assert get_current_schema() == "bar"
    assert get_current_schema() == PUBLIC_SCHEMA_NAME


@pytest.mark.django_db
def test_tenant_middleware_sets_request_tenant(client):
    tenant = Tenant.objects.create(name="Baz Org", slug="baz", schema_name="baz")
    create_schema("baz")
    Domain.objects.create(tenant=tenant, domain="baz.acme.dev", is_primary=True)

    res = client.get("/healthz", HTTP_HOST="baz.acme.dev")
    assert res.status_code == 200
    assert getattr(res.wsgi_request, "tenant") == tenant
