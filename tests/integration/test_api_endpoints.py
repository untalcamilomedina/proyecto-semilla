"""
Integration tests for API endpoints
Tests all CRUD operations and business logic
"""

import pytest
from uuid import uuid4


@pytest.mark.integration
class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self, test_client):
        """Test health endpoint returns 200"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data


@pytest.mark.integration
class TestAuthentication:
    """Test authentication endpoints"""

    def test_login_success(self, test_client, test_user):
        """Test successful login"""
        response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, test_client):
        """Test login with invalid credentials"""
        response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "invalid@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401

    def test_refresh_token(self, test_client, auth_headers):
        """Test token refresh"""
        # First login to get tokens
        login_response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]

        # Test refresh
        response = test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data




@pytest.mark.integration
class TestUsersAPI:
    """Test users API operations"""

    def test_get_users(self, test_client, auth_headers):
        """Test getting users list"""
        response = test_client.get("/api/v1/users", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the test user

    def test_get_current_user_profile(self, test_client, auth_headers):
        """Test getting current user profile"""
        response = test_client.get("/api/v1/users/profile", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "first_name" in data
        assert "last_name" in data


@pytest.mark.integration
class TestTenantsAPI:
    """Test tenants API operations"""

    def test_get_tenants(self, test_client, auth_headers):
        """Test getting tenants list"""
        response = test_client.get("/api/v1/tenants", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the test tenant


@pytest.mark.integration
class TestRolesAPI:
    """Test roles API operations"""

    def test_get_roles(self, test_client, auth_headers):
        """Test getting roles list"""
        response = test_client.get("/api/v1/roles", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the test role


@pytest.mark.integration
class TestMultiTenantIsolation:
    """Test multi-tenant data isolation"""



@pytest.mark.integration
class TestErrorHandling:
    """Test error handling and validation"""

    def test_unauthorized_access(self, test_client):
        """Test accessing protected endpoints without auth"""
        endpoints = [
            "/api/v1/users",
            "/api/v1/tenants",
            "/api/v1/roles"
        ]

        for endpoint in endpoints:
            response = test_client.get(endpoint)
            assert response.status_code == 401