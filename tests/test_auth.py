"""
Tests for authentication endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login with valid credentials"""
    login_data = {
        "username": "admin@proyecto-semilla.com",
        "password": "admin123"
    }

    response = await client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # Verify token format (basic check)
    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)
    assert len(data["access_token"]) > 100  # JWT tokens are long
    assert len(data["refresh_token"]) > 100


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials"""
    login_data = {
        "username": "admin@proyecto-semilla.com",
        "password": "wrongpassword"
    }

    response = await client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == 400
    data = response.json()
    assert "Incorrect email or password" in data["detail"]


@pytest.mark.asyncio
@pytest.mark.auth
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent user"""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "password123"
    }

    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 400
    data = response.json()
    assert "Incorrect email or password" in data["detail"]


@pytest.mark.asyncio
async def test_login_missing_fields(client: AsyncClient):
    """Test login with missing required fields"""
    # Missing password
    login_data = {"username": "admin@proyecto-semilla.com"}

    response = await client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 422  # Validation error

    # Missing username
    login_data = {"password": "admin123"}

    response = await client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    """Test token refresh functionality"""
    # First login to get tokens
    login_data = {
        "username": "admin@proyecto-semilla.com",
        "password": "admin123"
    }

    login_response = await client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    # Now test refresh
    refresh_data = {"refresh_token": refresh_token}

    response = await client.post("/api/v1/auth/refresh", json=refresh_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # Verify new tokens are different from old ones
    assert data["access_token"] != login_response.json()["access_token"]
    assert data["refresh_token"] != refresh_token


@pytest.mark.asyncio
@pytest.mark.auth
async def test_refresh_token_invalid(client: AsyncClient):
    """Test refresh with invalid token"""
    refresh_data = {"refresh_token": "invalid_token"}

    response = await client.post("/api/v1/auth/refresh", json=refresh_data)

    assert response.status_code == 401
    data = response.json()
    assert "Invalid or expired refresh token" in data["detail"]


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    """Test logout functionality"""
    # First login
    login_data = {
        "username": "admin@proyecto-semilla.com",
        "password": "admin123"
    }

    login_response = await client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    # Now logout
    logout_data = {"refresh_token": refresh_token}

    response = await client.post("/api/v1/auth/logout", json=logout_data)

    assert response.status_code == 200
    data = response.json()
    assert "Successfully logged out" in data["message"]

    # Try to refresh with the same token (should fail)
    refresh_data = {"refresh_token": refresh_token}
    refresh_response = await client.post("/api/v1/auth/refresh", json=refresh_data)

    assert refresh_response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.auth
async def test_me_endpoint(client: AsyncClient, auth_headers: dict):
    """Test /me endpoint returns current user info"""
    response = await client.get("/api/v1/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # Verify user data structure
    required_fields = ["id", "email", "first_name", "last_name", "full_name",
                      "is_active", "is_verified", "tenant_id", "role_ids",
                      "created_at", "updated_at"]

    for field in required_fields:
        assert field in data

    # Verify specific values
    assert data["email"] == "admin@proyecto-semilla.com"
    assert data["first_name"] == "Super"
    assert data["last_name"] == "Admin"
    assert data["full_name"] == "Super Admin"
    assert data["is_active"] is True
    assert data["is_verified"] is True


@pytest.mark.asyncio
@pytest.mark.auth
async def test_me_endpoint_unauthorized(client: AsyncClient):
    """Test /me endpoint without authentication"""
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401
    data = response.json()
    assert "Authentication required" in data["detail"]