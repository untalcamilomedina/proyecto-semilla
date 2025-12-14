import pytest
import uuid

from django.db import connection
from rest_framework.test import APIClient

from api.models import ApiKey
from config.settings.plugins import ENABLE_COMMUNITY, ENABLE_LMS, ENABLE_MCP
from core.models import Membership, Role, User
from core.services.seed import seed_default_roles
from multitenant.models import Domain, Tenant
from multitenant.schema import PUBLIC_SCHEMA_NAME, create_schema, schema_context


@pytest.mark.django_db(transaction=True)
def test_lms_course_crud():
    if not ENABLE_LMS:
        pytest.skip("LMS module not enabled")
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    with schema_context(PUBLIC_SCHEMA_NAME):
        slug = f"orglms-{uuid.uuid4().hex[:8]}"
        tenant_public = Tenant.objects.create(name="Org LMS", slug=slug, schema_name=slug)
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
            username="lmsadmin", email="lmsadmin@example.com", password="pass1234"
        )
        Membership.objects.create(user=user, organization=tenant_local, role=owner_role)
        _key, plain = ApiKey.generate(organization=tenant_local, user=user, name="default")

    client = APIClient()
    payload = {"title": "Course 101", "description": "Intro", "is_published": False}

    res = client.post(
        "/api/v1/lms/courses/",
        payload,
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 201
    course_id = res.data["id"]
    assert res.data["title"] == payload["title"]

    res = client.get(
        "/api/v1/lms/courses/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["count"] == 1
    assert res.data["results"][0]["id"] == course_id

    res = client.get(
        f"/api/v1/lms/courses/{course_id}/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["id"] == course_id

    res = client.patch(
        f"/api/v1/lms/courses/{course_id}/",
        {"title": "Course 102", "is_published": True},
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["title"] == "Course 102"
    assert res.data["is_published"] is True

    res = client.delete(
        f"/api/v1/lms/courses/{course_id}/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 204

    res = client.get(
        f"/api/v1/lms/courses/{course_id}/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_lms_enrollment_create():
    if not ENABLE_LMS:
        pytest.skip("LMS module not enabled")
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    with schema_context(PUBLIC_SCHEMA_NAME):
        slug = f"orglms2-{uuid.uuid4().hex[:8]}"
        tenant_public = Tenant.objects.create(name="Org LMS2", slug=slug, schema_name=slug)
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
            username="lmsuser", email="lmsuser@example.com", password="pass1234"
        )
        Membership.objects.create(user=user, organization=tenant_local, role=owner_role)
        _key, plain = ApiKey.generate(organization=tenant_local, user=user, name="default")

    client = APIClient()
    course_payload = {"title": "Course A", "description": "", "is_published": True}

    res = client.post(
        "/api/v1/lms/courses/",
        course_payload,
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 201
    course_id = res.data["id"]

    res = client.post(
        "/api/v1/lms/enrollments/",
        {"user": user.id, "course": course_id},
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 201
    assert res.data["user"] == user.id
    assert res.data["course"] == course_id
    assert res.data["progress"] == 0


@pytest.mark.django_db(transaction=True)
def test_lms_requires_authentication():
    if not ENABLE_LMS:
        pytest.skip("LMS module not enabled")
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    with schema_context(PUBLIC_SCHEMA_NAME):
        slug = f"orglms3-{uuid.uuid4().hex[:8]}"
        tenant_public = Tenant.objects.create(name="Org LMS3", slug=slug, schema_name=slug)
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
            username="lmsanon", email="lmsanon@example.com", password="pass1234"
        )
        Membership.objects.create(user=user, organization=tenant_local, role=owner_role)
        ApiKey.generate(organization=tenant_local, user=user, name="default")

    client = APIClient()
    res = client.get("/api/v1/lms/courses/", HTTP_HOST=f"{slug}.acme.dev")
    assert res.status_code in {401, 403}


@pytest.mark.django_db(transaction=True)
def test_community_forum_crud():
    if not ENABLE_COMMUNITY:
        pytest.skip("Community module not enabled")
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    with schema_context(PUBLIC_SCHEMA_NAME):
        slug = f"orgcom-{uuid.uuid4().hex[:8]}"
        tenant_public = Tenant.objects.create(name="Org Community", slug=slug, schema_name=slug)
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
            username="comadmin", email="comadmin@example.com", password="pass1234"
        )
        Membership.objects.create(user=user, organization=tenant_local, role=owner_role)
        _key, plain = ApiKey.generate(organization=tenant_local, user=user, name="default")

    client = APIClient()
    payload = {"name": "General", "description": "General discussion", "is_active": True}

    res = client.post(
        "/api/v1/community/forums/",
        payload,
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 201
    forum_id = res.data["id"]
    assert res.data["name"] == payload["name"]

    res = client.get(
        "/api/v1/community/forums/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["count"] == 1
    assert res.data["results"][0]["id"] == forum_id

    res = client.get(
        f"/api/v1/community/forums/{forum_id}/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["id"] == forum_id

    res = client.patch(
        f"/api/v1/community/forums/{forum_id}/",
        {"name": "General 2", "is_active": False},
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["name"] == "General 2"
    assert res.data["is_active"] is False

    res = client.delete(
        f"/api/v1/community/forums/{forum_id}/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 204

    res = client.get(
        f"/api/v1/community/forums/{forum_id}/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_community_post_requires_topic():
    if not ENABLE_COMMUNITY:
        pytest.skip("Community module not enabled")
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    with schema_context(PUBLIC_SCHEMA_NAME):
        slug = f"orgcom2-{uuid.uuid4().hex[:8]}"
        tenant_public = Tenant.objects.create(name="Org Community2", slug=slug, schema_name=slug)
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
            username="composter", email="composter@example.com", password="pass1234"
        )
        Membership.objects.create(user=user, organization=tenant_local, role=owner_role)
        _key, plain = ApiKey.generate(organization=tenant_local, user=user, name="default")

    client = APIClient()
    payload = {"topic": 999999, "author": user.id, "content": "Hello world"}

    res = client.post(
        "/api/v1/community/posts/",
        payload,
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 400
    assert "topic" in res.data


@pytest.mark.django_db(transaction=True)
def test_mcp_server_crud():
    if not ENABLE_MCP:
        pytest.skip("MCP module not enabled")
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    with schema_context(PUBLIC_SCHEMA_NAME):
        slug = f"orgmcp-{uuid.uuid4().hex[:8]}"
        tenant_public = Tenant.objects.create(name="Org MCP", slug=slug, schema_name=slug)
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
            username="mcpadmin", email="mcpadmin@example.com", password="pass1234"
        )
        Membership.objects.create(user=user, organization=tenant_local, role=owner_role)
        _key, plain = ApiKey.generate(organization=tenant_local, user=user, name="default")

    client = APIClient()
    payload = {
        "name": "Test Server",
        "description": "A server",
        "endpoint_url": "https://example.com/mcp",
        "api_key_hash": "",
        "is_active": True,
    }

    res = client.post(
        "/api/v1/mcp/servers/",
        payload,
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 201
    server_id = res.data["id"]
    assert res.data["name"] == payload["name"]

    res = client.get(
        "/api/v1/mcp/servers/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["count"] == 1
    assert res.data["results"][0]["id"] == server_id

    res = client.get(
        f"/api/v1/mcp/servers/{server_id}/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["id"] == server_id

    res = client.patch(
        f"/api/v1/mcp/servers/{server_id}/",
        {"description": "Updated", "is_active": False},
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 200
    assert res.data["description"] == "Updated"
    assert res.data["is_active"] is False

    res = client.delete(
        f"/api/v1/mcp/servers/{server_id}/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 204

    res = client.get(
        f"/api/v1/mcp/servers/{server_id}/",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_mcp_tool_requires_server():
    if not ENABLE_MCP:
        pytest.skip("MCP module not enabled")
    if connection.vendor != "postgresql":
        pytest.skip("Schema multitenancy requires Postgres")

    with schema_context(PUBLIC_SCHEMA_NAME):
        slug = f"orgmcp2-{uuid.uuid4().hex[:8]}"
        tenant_public = Tenant.objects.create(name="Org MCP2", slug=slug, schema_name=slug)
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
            username="mcptool", email="mcptool@example.com", password="pass1234"
        )
        Membership.objects.create(user=user, organization=tenant_local, role=owner_role)
        _key, plain = ApiKey.generate(organization=tenant_local, user=user, name="default")

    client = APIClient()
    payload = {"server": 999999, "name": "Search", "description": "", "input_schema": {}}

    res = client.post(
        "/api/v1/mcp/tools/",
        payload,
        format="json",
        HTTP_HOST=f"{slug}.acme.dev",
        HTTP_AUTHORIZATION=f"Bearer {plain}",
    )
    assert res.status_code == 400
    assert "server" in res.data

