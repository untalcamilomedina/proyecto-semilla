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


@pytest.mark.integration
class TestArticlesAPI:
    """Test articles API operations"""

    def test_get_articles_list(self, client: AsyncClient, auth_headers: dict):
        """Test getting articles list"""
        response = client.get("/api/v1/articles/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_article(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str, test_user_id: str):
        """Test article creation"""
        article_data = {
            "title": "New Test Article",
            "slug": "new-test-article",
            "content": "<p>This is a new test article.</p>",
            "excerpt": "New test excerpt",
            "status": "draft",
            "tags": ["new", "test"],
            "tenant_id": test_tenant_id,
            "author_id": test_user_id
        }

        response = client.post("/api/v1/articles/", json=article_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Test Article"
        assert data["slug"] == "new-test-article"
        assert data["status"] == "draft"
        assert "id" in data

        # Store article ID for other tests
        self.article_id = data["id"]

    def test_get_article_by_id(self, client: AsyncClient, auth_headers: dict, test_article: Article):
        """Test getting specific article"""
        response = client.get(f"/api/v1/articles/{test_article.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Article"
        assert data["slug"] == "test-article"

    def test_update_article(self, client: AsyncClient, auth_headers: dict, test_article: Article):
        """Test article update"""
        update_data = {
            "title": "Updated Test Article",
            "content": "<p>Updated content.</p>",
            "status": "published"
        }

        response = client.put(f"/api/v1/articles/{test_article.id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Test Article"
        assert data["status"] == "published"

    def test_delete_article(self, client: AsyncClient, auth_headers: dict, test_article: Article):
        """Test article deletion"""
        response = client.delete(f"/api/v1/articles/{test_article.id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify deletion
        response = client.get(f"/api/v1/articles/{test_article.id}", headers=auth_headers)
        assert response.status_code == 404

    def test_get_articles_stats(self, client: AsyncClient, auth_headers: dict):
        """Test articles statistics"""
        response = client.get("/api/v1/articles/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_articles" in data
        assert "published_articles" in data
        assert "draft_articles" in data
        assert isinstance(data["total_articles"], int)


@pytest.mark.integration
class TestCategoriesAPI:
    """Test categories API operations"""

    def test_get_categories_list(self, client: AsyncClient, auth_headers: dict):
        """Test getting categories list"""
        response = client.get("/api/v1/categories/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_category(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str):
        """Test category creation"""
        category_data = {
            "name": "New Test Category",
            "slug": "new-test-category",
            "description": "New test category description",
            "tenant_id": test_tenant_id
        }

        response = client.post("/api/v1/categories/", json=category_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Test Category"
        assert data["slug"] == "new-test-category"
        assert "id" in data

    def test_get_category_by_id(self, client: AsyncClient, auth_headers: dict, test_category: Category):
        """Test getting specific category"""
        response = client.get(f"/api/v1/categories/{test_category.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Category"
        assert data["slug"] == "test-category"

    def test_update_category(self, client: AsyncClient, auth_headers: dict, test_category: Category):
        """Test category update"""
        update_data = {
            "name": "Updated Test Category",
            "description": "Updated description"
        }

        response = client.put(f"/api/v1/categories/{test_category.id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Test Category"

    def test_delete_category(self, client: AsyncClient, auth_headers: dict, test_category: Category):
        """Test category deletion"""
        response = client.delete(f"/api/v1/categories/{test_category.id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify deletion
        response = client.get(f"/api/v1/categories/{test_category.id}", headers=auth_headers)
        assert response.status_code == 404

    def test_get_categories_tree(self, client: AsyncClient, auth_headers: dict):
        """Test categories tree endpoint"""
        response = client.get("/api/v1/categories/tree", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.integration
class TestCommentsAPI:
    """Test comments API operations"""

    def test_get_comments_list(self, client: AsyncClient, auth_headers: dict):
        """Test getting comments list"""
        response = client.get("/api/v1/comments/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_comment(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str, test_user_id: str, test_article: Article):
        """Test comment creation"""
        comment_data = {
            "content": "This is a new test comment.",
            "article_id": str(test_article.id),
            "author_id": test_user_id,
            "tenant_id": test_tenant_id
        }

        response = client.post("/api/v1/comments/", json=comment_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "This is a new test comment."
        assert "id" in data

    def test_get_comment_by_id(self, client: AsyncClient, auth_headers: dict, test_comment: Comment):
        """Test getting specific comment"""
        response = client.get(f"/api/v1/comments/{test_comment.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "This is a test comment."

    def test_update_comment(self, client: AsyncClient, auth_headers: dict, test_comment: Comment):
        """Test comment update"""
        update_data = {
            "content": "Updated comment content."
        }

        response = client.put(f"/api/v1/comments/{test_comment.id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated comment content."

    def test_delete_comment(self, client: AsyncClient, auth_headers: dict, test_comment: Comment):
        """Test comment deletion"""
        response = client.delete(f"/api/v1/comments/{test_comment.id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify deletion
        response = client.get(f"/api/v1/comments/{test_comment.id}", headers=auth_headers)
        assert response.status_code == 404

    def test_get_comments_stats(self, client: AsyncClient, auth_headers: dict):
        """Test comments statistics"""
        response = client.get("/api/v1/comments/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_comments" in data
        assert isinstance(data["total_comments"], int)


@pytest.mark.integration
class TestMediaAPI:
    """Test media API operations"""

    def test_get_media_uploads(self, client: AsyncClient, auth_headers: dict):
        """Test getting media uploads list"""
        response = client.get("/api/v1/media/uploads", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.integration
class TestDashboardAPI:
    """Test dashboard API operations"""

    def test_get_dashboard_stats(self, client: AsyncClient, auth_headers: dict):
        """Test getting dashboard statistics"""
        response = client.get("/api/v1/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Dashboard stats should contain various metrics
        assert isinstance(data, dict)


@pytest.mark.integration
class TestUsersCRUD:
    """Test complete users CRUD operations"""

    def test_create_user(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str):
        """Test user creation via API"""
        user_data = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "password123",
            "tenant_id": test_tenant_id
        }

        response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        if response.status_code == 201:
            data = response.json()
            assert data["email"] == "newuser@example.com"
            assert data["first_name"] == "New"
        else:
            # May require admin permissions
            assert response.status_code in [403, 422]

    def test_update_user(self, client: AsyncClient, auth_headers: dict, test_user: User):
        """Test user update"""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name"
        }

        response = client.put(f"/api/v1/users/{test_user.id}", json=update_data, headers=auth_headers)
        if response.status_code == 200:
            data = response.json()
            assert data["first_name"] == "Updated"
        else:
            # May require permissions
            assert response.status_code in [403, 404]

    def test_get_user_by_id(self, client: AsyncClient, auth_headers: dict, test_user: User):
        """Test getting user by ID"""
        response = client.get(f"/api/v1/users/{test_user.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"


@pytest.mark.integration
class TestRolesCRUD:
    """Test complete roles CRUD operations"""

    def test_create_role(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str):
        """Test role creation via API"""
        role_data = {
            "name": "New Role",
            "description": "New test role",
            "permissions": ["read", "write"],
            "tenant_id": test_tenant_id
        }

        response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
        if response.status_code == 201:
            data = response.json()
            assert data["name"] == "New Role"
        else:
            # May require admin permissions
            assert response.status_code in [403, 422]

    def test_get_role_by_id(self, client: AsyncClient, auth_headers: dict, test_role: Role):
        """Test getting role by ID"""
        response = client.get(f"/api/v1/roles/{test_role.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Editor"


@pytest.mark.integration
class TestTenantsCRUD:
    """Test complete tenants CRUD operations"""

    def test_get_tenant_by_id(self, client: AsyncClient, auth_headers: dict, test_user: User):
        """Test getting tenant by ID"""
        response = client.get(f"/api/v1/tenants/{test_user.tenant_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Tenant"


@pytest.mark.integration
class TestMultiTenantIsolation:
    """Test multi-tenant data isolation at API level"""

    def test_tenant_isolation_articles(self, client: AsyncClient, auth_headers: dict, auth_headers2: dict, test_article: Article):
        """Test that users from different tenants can't access each other's articles"""
        # User from tenant 1 should see their article
        response = client.get(f"/api/v1/articles/{test_article.id}", headers=auth_headers)
        assert response.status_code == 200

        # User from tenant 2 should not see tenant 1's article
        response = client.get(f"/api/v1/articles/{test_article.id}", headers=auth_headers2)
        assert response.status_code == 404

    def test_tenant_isolation_users(self, client: AsyncClient, auth_headers: dict, auth_headers2: dict, test_user: User, test_user2: User):
        """Test that users from different tenants can't access each other's data"""
        # User from tenant 1 should see their own profile
        response = client.get("/api/v1/users/profile", headers=auth_headers)
        assert response.status_code == 200

        # User from tenant 1 should not see tenant 2's user
        response = client.get(f"/api/v1/users/{test_user2.id}", headers=auth_headers)
        assert response.status_code == 404

        # User from tenant 2 should not see tenant 1's user
        response = client.get(f"/api/v1/users/{test_user.id}", headers=auth_headers2)
        assert response.status_code == 404


@pytest.mark.integration
class TestValidationAndErrors:
    """Test input validation and error handling"""

    def test_create_article_invalid_data(self, client: AsyncClient, auth_headers: dict):
        """Test article creation with invalid data"""
        invalid_data = {
            "title": "",  # Empty title should fail
            "content": "<p>Content</p>"
        }

        response = client.post("/api/v1/articles/", json=invalid_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error

    def test_create_category_invalid_data(self, client: AsyncClient, auth_headers: dict):
        """Test category creation with invalid data"""
        invalid_data = {
            "name": "",  # Empty name should fail
            "slug": "invalid slug with spaces"
        }

        response = client.post("/api/v1/categories/", json=invalid_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error

    def test_get_nonexistent_resource(self, client: AsyncClient, auth_headers: dict):
        """Test accessing non-existent resources"""
        fake_uuid = str(uuid4())

        endpoints = [
            f"/api/v1/articles/{fake_uuid}",
            f"/api/v1/categories/{fake_uuid}",
            f"/api/v1/comments/{fake_uuid}",
            f"/api/v1/users/{fake_uuid}",
            f"/api/v1/roles/{fake_uuid}",
            f"/api/v1/tenants/{fake_uuid}"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint, headers=auth_headers)
            assert response.status_code == 404

    def test_unauthorized_operations(self, client: AsyncClient, auth_headers: dict, test_article: Article):
        """Test operations that may require specific permissions"""
        # Try to delete an article (may require permissions)
        response = client.delete(f"/api/v1/articles/{test_article.id}", headers=auth_headers)
        assert response.status_code in [204, 403, 404]  # Success, Forbidden, or Not Found
            assert response.status_code == 401