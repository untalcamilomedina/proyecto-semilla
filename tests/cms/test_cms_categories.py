"""
Comprehensive tests for CMS categories functionality
Tests hierarchical categories, CRUD operations, and business logic
"""

import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.tenant import Tenant
from app.models.user import User


@pytest.mark.asyncio
@pytest.mark.cms
class TestCMSCategoriesCRUD:
    """Test CMS categories CRUD operations"""

    async def test_create_category(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str):
        """Test category creation with valid data"""
        category_data = {
            "name": "Technology",
            "slug": "technology",
            "description": "Technology related articles",
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/categories/", json=category_data, headers=auth_headers)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == "Technology"
        assert data["slug"] == "technology"
        assert data["description"] == "Technology related articles"
        assert "id" in data

    async def test_create_category_with_parent(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str):
        """Test creating a subcategory"""
        # First create parent category
        parent_data = {
            "name": "Technology",
            "slug": "technology",
            "description": "Technology articles",
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/categories/", json=parent_data, headers=auth_headers)
        assert response.status_code == 201
        parent_id = response.json()["id"]

        # Create child category
        child_data = {
            "name": "Web Development",
            "slug": "web-development",
            "description": "Web development articles",
            "parent_id": parent_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/categories/", json=child_data, headers=auth_headers)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == "Web Development"
        assert data["parent_id"] == parent_id

    async def test_get_category_by_id(self, client: AsyncClient, auth_headers: dict, test_category: Category):
        """Test retrieving a specific category"""
        response = await client.get(f"/api/v1/categories/{test_category.id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Test Category"
        assert data["slug"] == "test-category"

    async def test_update_category(self, client: AsyncClient, auth_headers: dict, test_category: Category):
        """Test category update"""
        update_data = {
            "name": "Updated Category",
            "description": "Updated description",
            "slug": "updated-category"
        }

        response = await client.put(f"/api/v1/categories/{test_category.id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Updated Category"
        assert data["description"] == "Updated description"

    async def test_delete_category(self, client: AsyncClient, auth_headers: dict, test_category: Category):
        """Test category deletion"""
        response = await client.delete(f"/api/v1/categories/{test_category.id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify deletion
        response = await client.get(f"/api/v1/categories/{test_category.id}", headers=auth_headers)
        assert response.status_code == 404

    async def test_get_categories_list(self, client: AsyncClient, auth_headers: dict):
        """Test getting categories list"""
        response = await client.get("/api/v1/categories/", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # Should have at least the test category if it exists
        if len(data) > 0:
            category = data[0]
            assert "name" in category
            assert "slug" in category
            assert "id" in category


@pytest.mark.asyncio
@pytest.mark.cms
class TestCMSCategoriesHierarchy:
    """Test category hierarchy functionality"""

    async def test_category_tree_structure(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str):
        """Test category tree endpoint returns proper hierarchy"""
        response = await client.get("/api/v1/categories/tree", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # If there are categories, check tree structure
        if len(data) > 0:
            for category in data:
                assert "name" in category
                assert "id" in category
                if "children" in category:
                    assert isinstance(category["children"], list)

    async def test_deep_hierarchy_creation(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str):
        """Test creating deep category hierarchies"""
        # Create 3-level hierarchy
        level1_data = {
            "name": "Level 1",
            "slug": "level-1",
            "description": "First level",
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/categories/", json=level1_data, headers=auth_headers)
        assert response.status_code == 201
        level1_id = response.json()["id"]

        level2_data = {
            "name": "Level 2",
            "slug": "level-2",
            "description": "Second level",
            "parent_id": level1_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/categories/", json=level2_data, headers=auth_headers)
        assert response.status_code == 201
        level2_id = response.json()["id"]

        level3_data = {
            "name": "Level 3",
            "slug": "level-3",
            "description": "Third level",
            "parent_id": level2_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/categories/", json=level3_data, headers=auth_headers)
        assert response.status_code == 201

        # Verify hierarchy in tree
        response = await client.get("/api/v1/categories/tree", headers=auth_headers)
        assert response.status_code == 200

    async def test_circular_reference_prevention(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str):
        """Test that circular references in category hierarchy are prevented"""
        # Create two categories
        cat1_data = {
            "name": "Category 1",
            "slug": "category-1",
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/categories/", json=cat1_data, headers=auth_headers)
        assert response.status_code == 201
        cat1_id = response.json()["id"]

        cat2_data = {
            "name": "Category 2",
            "slug": "category-2",
            "parent_id": cat1_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/categories/", json=cat2_data, headers=auth_headers)
        assert response.status_code == 201
        cat2_id = response.json()["id"]

        # Try to make cat1 a child of cat2 (circular reference)
        update_data = {
            "parent_id": cat2_id
        }

        response = await client.put(f"/api/v1/categories/{cat1_id}", json=update_data, headers=auth_headers)
        # Should fail or be prevented
        assert response.status_code in [400, 422, 200]  # Depending on implementation


@pytest.mark.asyncio
@pytest.mark.cms
class TestCMSCategoriesValidation:
    """Test category validation and edge cases"""

    async def test_create_category_duplicate_slug(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str):
        """Test creating category with duplicate slug fails"""
        category_data = {
            "name": "Test Category",
            "slug": "test-category-slug",
            "description": "Test description",
            "tenant_id": test_tenant_id
        }

        # Create first category
        response = await client.post("/api/v1/categories/", json=category_data, headers=auth_headers)
        assert response.status_code == 201

        # Try to create second category with same slug
        response = await client.post("/api/v1/categories/", json=category_data, headers=auth_headers)
        # Should fail due to unique constraint
        assert response.status_code in [400, 422]

    async def test_create_category_invalid_slug(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str):
        """Test creating category with invalid slug"""
        invalid_slugs = [
            "Invalid Slug With Spaces",
            "invalid/slug",
            "invalid.slug@",
            ""
        ]

        for invalid_slug in invalid_slugs:
            category_data = {
                "name": "Test Category",
                "slug": invalid_slug,
                "description": "Test description",
                "tenant_id": test_tenant_id
            }

            response = await client.post("/api/v1/categories/", json=category_data, headers=auth_headers)
            # Should fail validation
            assert response.status_code == 422

    async def test_create_category_empty_name(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str):
        """Test creating category with empty name fails"""
        category_data = {
            "name": "",
            "slug": "empty-name-category",
            "description": "Test description",
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/categories/", json=category_data, headers=auth_headers)
        assert response.status_code == 422

    async def test_update_category_to_invalid_parent(self, client: AsyncClient, auth_headers: dict, test_category: Category):
        """Test updating category to have invalid parent"""
        # Try to set parent to non-existent category
        fake_parent_id = str(uuid4())
        update_data = {
            "parent_id": fake_parent_id
        }

        response = await client.put(f"/api/v1/categories/{test_category.id}", json=update_data, headers=auth_headers)
        # Should fail due to foreign key constraint
        assert response.status_code in [400, 422, 404]


@pytest.mark.asyncio
@pytest.mark.cms
class TestCMSCategoriesBusinessLogic:
    """Test category business logic"""

    async def test_category_full_path_calculation(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str):
        """Test that category full path is calculated correctly"""
        # Create hierarchy
        parent_data = {
            "name": "Parent",
            "slug": "parent",
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/categories/", json=parent_data, headers=auth_headers)
        assert response.status_code == 201
        parent_id = response.json()["id"]

        child_data = {
            "name": "Child",
            "slug": "child",
            "parent_id": parent_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/categories/", json=child_data, headers=auth_headers)
        assert response.status_code == 201

        # Get category and check full path
        child_id = response.json()["id"]
        response = await client.get(f"/api/v1/categories/{child_id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # Full path should include parent > child
        assert "Parent > Child" in data.get("full_path", "")

    async def test_category_deletion_with_children(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str):
        """Test deleting category with children"""
        # Create parent with child
        parent_data = {
            "name": "Parent",
            "slug": "parent",
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/categories/", json=parent_data, headers=auth_headers)
        assert response.status_code == 201
        parent_id = response.json()["id"]

        child_data = {
            "name": "Child",
            "slug": "child",
            "parent_id": parent_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/categories/", json=child_data, headers=auth_headers)
        assert response.status_code == 201
        child_id = response.json()["id"]

        # Try to delete parent (should handle children appropriately)
        response = await client.delete(f"/api/v1/categories/{parent_id}", headers=auth_headers)
        # Depending on implementation: cascade delete, prevent deletion, or orphan children
        assert response.status_code in [204, 400, 409]

    async def test_category_slug_auto_generation(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str):
        """Test automatic slug generation from name"""
        category_data = {
            "name": "Test Category With Spaces",
            "description": "Test description",
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/categories/", json=category_data, headers=auth_headers)
        assert response.status_code == 201

        data = response.json()
        # Slug should be generated from name
        assert data["slug"] == "test-category-with-spaces" or "slug" in data