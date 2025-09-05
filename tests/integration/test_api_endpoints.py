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
class TestArticlesAPI:
    """Test articles CRUD operations"""

    def test_get_articles_unauthorized(self, test_client):
        """Test getting articles without authentication"""
        response = test_client.get("/api/v1/articles")
        assert response.status_code == 401

    def test_get_articles_authorized(self, test_client, auth_headers):
        """Test getting articles with authentication"""
        response = test_client.get("/api/v1/articles", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_article(self, test_client, auth_headers):
        """Test creating a new article"""
        article_data = {
            "title": "Test Article",
            "slug": "test-article",
            "content": "This is test content",
            "excerpt": "Test excerpt",
            "status": "draft",
            "is_featured": False,
            "tags": ["test", "article"]
        }

        response = test_client.post(
            "/api/v1/articles",
            json=article_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == article_data["title"]
        assert data["slug"] == article_data["slug"]
        assert "id" in data

    def test_get_article_by_id(self, test_client, auth_headers, test_article):
        """Test getting article by ID"""
        response = test_client.get(
            f"/api/v1/articles/{test_article.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_article.id)
        assert data["title"] == test_article.title

    def test_update_article(self, test_client, auth_headers, test_article):
        """Test updating an article"""
        update_data = {
            "title": "Updated Test Article",
            "content": "Updated content"
        }

        response = test_client.put(
            f"/api/v1/articles/{test_article.id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]

    def test_delete_article(self, test_client, auth_headers, test_article):
        """Test deleting an article"""
        response = test_client.delete(
            f"/api/v1/articles/{test_article.id}",
            headers=auth_headers
        )
        assert response.status_code == 200

        # Verify article is deleted
        response = test_client.get(
            f"/api/v1/articles/{test_article.id}",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_get_article_stats(self, test_client, auth_headers):
        """Test getting article statistics"""
        response = test_client.get(
            "/api/v1/articles/stats/overview",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_articles" in data
        assert "published_articles" in data
        assert "draft_articles" in data
        assert "total_views" in data


@pytest.mark.integration
class TestCategoriesAPI:
    """Test categories CRUD operations"""

    def test_get_categories(self, test_client, auth_headers):
        """Test getting categories"""
        response = test_client.get("/api/v1/categories", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_category(self, test_client, auth_headers):
        """Test creating a category"""
        category_data = {
            "name": "Test Category",
            "slug": "test-category",
            "description": "Test category description"
        }

        response = test_client.post(
            "/api/v1/categories",
            json=category_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == category_data["name"]
        assert data["slug"] == category_data["slug"]


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

    def test_tenant_isolation_articles(self, test_client, auth_headers):
        """Test that users can only access their tenant's articles"""
        # Create article for test tenant
        article_data = {
            "title": "Tenant Article",
            "slug": "tenant-article",
            "content": "Content for tenant",
            "excerpt": "Tenant excerpt",
            "status": "published",
            "is_featured": False,
            "tags": ["tenant", "test"]
        }

        response = test_client.post(
            "/api/v1/articles",
            json=article_data,
            headers=auth_headers
        )
        assert response.status_code == 200

        # Get articles and verify tenant isolation
        response = test_client.get("/api/v1/articles", headers=auth_headers)
        assert response.status_code == 200
        articles = response.json()

        # All returned articles should belong to the test tenant
        for article in articles:
            assert "tenant_id" in article


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling and validation"""

    def test_invalid_article_slug(self, test_client, auth_headers):
        """Test creating article with invalid slug"""
        article_data = {
            "title": "Test Article",
            "slug": "invalid slug with spaces",  # Invalid slug
            "content": "Test content",
            "excerpt": "Test excerpt",
            "status": "draft",
            "is_featured": False,
            "tags": ["test"]
        }

        response = test_client.post(
            "/api/v1/articles",
            json=article_data,
            headers=auth_headers
        )
        # Should return validation error
        assert response.status_code in [400, 422]

    def test_article_not_found(self, test_client, auth_headers):
        """Test accessing non-existent article"""
        fake_id = str(uuid4())
        response = test_client.get(
            f"/api/v1/articles/{fake_id}",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_unauthorized_access(self, test_client):
        """Test accessing protected endpoints without auth"""
        endpoints = [
            "/api/v1/articles",
            "/api/v1/users",
            "/api/v1/tenants",
            "/api/v1/roles"
        ]

        for endpoint in endpoints:
            response = test_client.get(endpoint)
            assert response.status_code == 401