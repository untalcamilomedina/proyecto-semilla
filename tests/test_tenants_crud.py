"""
Tests for tenant CRUD operations
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.crud
async def test_create_tenant(client: AsyncClient, auth_headers: dict):
    """Test tenant creation"""
    tenant_data = {
        "name": "Test Tenant",
        "slug": "test-tenant-crud",
        "description": "Tenant created by CRUD test",
        "settings": '{"theme": "light", "features": ["auth", "users"]}',
        "is_active": True
    }

    response = await client.post(
        "/api/v1/tenants/",
        json=tenant_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert data["name"] == "Test Tenant"
    assert data["slug"] == "test-tenant-crud"
    assert data["description"] == "Tenant created by CRUD test"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "parent_tenant_id" in data

    # Verify timestamps are valid ISO format
    assert "T" in data["created_at"]
    assert "T" in data["updated_at"]


@pytest.mark.asyncio
@pytest.mark.crud
async def test_create_tenant_duplicate_slug(client: AsyncClient, auth_headers: dict):
    """Test creating tenant with duplicate slug fails"""
    # Create first tenant
    tenant_data = {
        "name": "First Tenant",
        "slug": "duplicate-slug",
        "description": "First tenant",
        "settings": "{}",
        "is_active": True
    }

    response1 = await client.post(
        "/api/v1/tenants/",
        json=tenant_data,
        headers=auth_headers
    )
    assert response1.status_code == 200

    # Try to create second tenant with same slug
    tenant_data2 = {
        "name": "Second Tenant",
        "slug": "duplicate-slug",  # Same slug
        "description": "Second tenant",
        "settings": "{}",
        "is_active": True
    }

    response2 = await client.post(
        "/api/v1/tenants/",
        json=tenant_data2,
        headers=auth_headers
    )

    assert response2.status_code == 400
    data = response2.json()
    assert "already exists" in data["detail"]


@pytest.mark.asyncio
@pytest.mark.crud
async def test_get_tenant_list(client: AsyncClient, auth_headers: dict):
    """Test tenant list retrieval"""
    response = await client.get("/api/v1/tenants/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 2  # At least the seed tenants

    # Verify structure of first tenant
    tenant = data[0]
    required_fields = ["id", "name", "slug", "description", "is_active",
                      "created_at", "updated_at", "parent_tenant_id", "settings"]

    for field in required_fields:
        assert field in tenant


@pytest.mark.asyncio
@pytest.mark.crud
async def test_get_tenant_by_id(client: AsyncClient, auth_headers: dict, test_tenant_id: str):
    """Test get tenant by ID"""
    response = await client.get(
        f"/api/v1/tenants/{test_tenant_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Verify tenant data
    assert data["id"] == test_tenant_id
    assert data["name"] == "Test Tenant"
    assert "user_count" in data
    assert "role_count" in data
    assert isinstance(data["user_count"], int)
    assert isinstance(data["role_count"], int)


@pytest.mark.asyncio
@pytest.mark.crud
async def test_get_tenant_not_found(client: AsyncClient, auth_headers: dict):
    """Test get tenant with non-existent ID"""
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = await client.get(
        f"/api/v1/tenants/{fake_id}",
        headers=auth_headers
    )

    assert response.status_code == 404
    data = response.json()
    assert "Tenant not found" in data["detail"]


@pytest.mark.asyncio
@pytest.mark.crud
async def test_update_tenant(client: AsyncClient, auth_headers: dict, test_tenant_id: str):
    """Test tenant update"""
    update_data = {
        "name": "Updated Test Tenant",
        "description": "Updated description for test tenant",
        "settings": '{"theme": "dark", "features": ["auth", "users", "billing"]}'
    }

    response = await client.put(
        f"/api/v1/tenants/{test_tenant_id}",
        json=update_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Verify updates were applied
    assert data["name"] == "Updated Test Tenant"
    assert data["description"] == "Updated description for test tenant"
    assert data["settings"] == '{"theme": "dark", "features": ["auth", "users", "billing"]}'

    # Verify timestamps
    assert "updated_at" in data
    assert "created_at" in data


@pytest.mark.asyncio
@pytest.mark.crud
async def test_update_tenant_partial(client: AsyncClient, auth_headers: dict, test_tenant_id: str):
    """Test partial tenant update"""
    # Only update name
    update_data = {"name": "Partially Updated Tenant"}

    response = await client.put(
        f"/api/v1/tenants/{test_tenant_id}",
        json=update_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "Partially Updated Tenant"
    # Other fields should remain unchanged
    assert data["slug"] == "test-tenant-fixture"


@pytest.mark.asyncio
@pytest.mark.crud
async def test_update_tenant_no_fields(client: AsyncClient, auth_headers: dict, test_tenant_id: str):
    """Test update tenant with no fields to update"""
    update_data = {}

    response = await client.put(
        f"/api/v1/tenants/{test_tenant_id}",
        json=update_data,
        headers=auth_headers
    )

    assert response.status_code == 400
    data = response.json()
    assert "No fields to update" in data["detail"]


@pytest.mark.asyncio
@pytest.mark.crud
async def test_delete_tenant(client: AsyncClient, auth_headers: dict, test_tenant_id: str):
    """Test tenant soft delete"""
    response = await client.delete(
        f"/api/v1/tenants/{test_tenant_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "successfully" in data["message"]

    # Verify tenant is marked as inactive
    get_response = await client.get(
        f"/api/v1/tenants/{test_tenant_id}",
        headers=auth_headers
    )

    assert get_response.status_code == 200
    tenant_data = get_response.json()
    assert tenant_data["is_active"] is False


@pytest.mark.asyncio
@pytest.mark.crud
async def test_delete_tenant_not_found(client: AsyncClient, auth_headers: dict):
    """Test delete tenant with non-existent ID"""
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = await client.delete(
        f"/api/v1/tenants/{fake_id}",
        headers=auth_headers
    )

    assert response.status_code == 404
    data = response.json()
    assert "Tenant not found" in data["detail"]


@pytest.mark.asyncio
@pytest.mark.crud
async def test_tenant_pagination(client: AsyncClient, auth_headers: dict):
    """Test tenant list pagination"""
    # Test with limit
    response = await client.get(
        "/api/v1/tenants/?limit=1",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1

    # Test with skip
    response2 = await client.get(
        "/api/v1/tenants/?skip=1&limit=1",
        headers=auth_headers
    )

    assert response2.status_code == 200
    data2 = response2.json()
    assert isinstance(data2, list)
    assert len(data2) == 1

    # Results should be different
    assert data[0]["id"] != data2[0]["id"]


@pytest.mark.asyncio
@pytest.mark.crud
async def test_tenant_unauthorized_access(client: AsyncClient):
    """Test tenant endpoints require authentication"""
    endpoints = [
        "/api/v1/tenants/",
        "/api/v1/tenants/123e4567-e89b-12d3-a456-426614174000"
    ]

    for endpoint in endpoints:
        # Test GET
        response = await client.get(endpoint)
        assert response.status_code == 401

        # Test POST
        if endpoint.endswith("/"):
            response = await client.post(endpoint, json={})
            assert response.status_code == 401

        # Test PUT
        if not endpoint.endswith("/"):
            response = await client.put(endpoint, json={})
            assert response.status_code == 401

        # Test DELETE
        if not endpoint.endswith("/"):
            response = await client.delete(endpoint)
            assert response.status_code == 401