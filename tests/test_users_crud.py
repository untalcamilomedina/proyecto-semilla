"""
Tests for user CRUD operations
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.core.config import settings


@pytest.mark.asyncio
@pytest.mark.crud
async def test_create_user(client: AsyncClient, auth_headers: dict, test_tenant_id: str):
    """Test user creation"""
    user_data = {
        "email": "newuser@example.com",
        "password": "password123",
        "first_name": "New",
        "last_name": "User",
        "tenant_id": test_tenant_id,
        "role_ids": [],
    }

    response = await client.post(
        "/api/v1/users/",
        json=user_data,
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()

    assert data["email"] == "newuser@example.com"
    assert data["first_name"] == "New"
    assert data["last_name"] == "User"
    assert data["full_name"] == "New User"
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.asyncio
@pytest.mark.crud
async def test_get_user_list(client: AsyncClient, auth_headers: dict):
    """Test user list retrieval"""
    response = await client.get("/api/v1/users/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
@pytest.mark.crud
async def test_get_user_by_id(client: AsyncClient, auth_headers: dict, test_user_id: str):
    """Test get user by ID"""
    response = await client.get(
        f"/api/v1/users/{test_user_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == test_user_id
    assert data["email"] == settings.TEST_USER_EMAIL


@pytest.mark.asyncio
@pytest.mark.crud
async def test_update_user(client: AsyncClient, auth_headers: dict, test_user_id: str):
    """Test user update"""
    update_data = {
        "first_name": "Updated",
        "last_name": "User",
    }

    response = await client.put(
        f"/api/v1/users/{test_user_id}",
        json=update_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["first_name"] == "Updated"
    assert data["last_name"] == "User"
    assert data["full_name"] == "Updated User"


@pytest.mark.asyncio
@pytest.mark.crud
async def test_delete_user(client: AsyncClient, auth_headers: dict, test_user_id: str):
    """Test user soft delete"""
    response = await client.delete(
        f"/api/v1/users/{test_user_id}",
        headers=auth_headers
    )

    assert response.status_code == 204

    # Verify user is marked as inactive
    get_response = await client.get(
        f"/api/v1/users/{test_user_id}",
        headers=auth_headers
    )

    assert get_response.status_code == 200
    user_data = get_response.json()
    assert user_data["is_active"] is False