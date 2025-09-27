"""
Unit tests for database models
Tests model creation, validation, and business logic
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.tenant import Tenant
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.article import Article
from app.models.category import Category
from app.models.comment import Comment
from app.models.audit_log import AuditLog
from app.models.refresh_token import RefreshToken
from app.models.system_user_flag import SystemUserFlag


@pytest.mark.asyncio
@pytest.mark.unit
class TestUserModel:
    """Test User model functionality"""

    async def test_user_creation(self, test_db: AsyncSession):
        """Test user model creation with valid data"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()

        user = User(
            tenant_id=tenant.id,
            email="test@example.com",
            hashed_password="hashed_password",
            first_name="Test",
            last_name="User",
            full_name="Test User"
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None

    async def test_user_has_permission_without_roles(self, test_db: AsyncSession):
        """Test user permission check when user has no roles"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()

        user = User(
            tenant_id=tenant.id,
            email="test@example.com",
            hashed_password="hashed_password",
            first_name="Test",
            last_name="User",
            full_name="Test User"
        )
        test_db.add(user)
        await test_db.commit()

        assert user.has_permission("admin") is False
        assert user.has_permission("read") is False

    async def test_user_has_permission_with_roles(self, test_db: AsyncSession):
        """Test user permission check with roles assigned"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()

        user = User(
            tenant_id=tenant.id,
            email="test@example.com",
            hashed_password="hashed_password",
            first_name="Test",
            last_name="User",
            full_name="Test User"
        )
        test_db.add(user)

        role = Role(
            tenant_id=tenant.id,
            name="Admin",
            permissions='["admin", "read", "write"]'
        )
        test_db.add(role)

        user_role = UserRole(user_id=user.id, role_id=role.id)
        test_db.add(user_role)

        await test_db.commit()

        assert user.has_permission("admin") is True
        assert user.has_permission("read") is True
        assert user.has_permission("write") is True
        assert user.has_permission("delete") is False


@pytest.mark.asyncio
@pytest.mark.unit
class TestTenantModel:
    """Test Tenant model functionality"""

    async def test_tenant_creation(self, test_db: AsyncSession):
        """Test tenant model creation"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()
        await test_db.refresh(tenant)

        assert tenant.id is not None
        assert tenant.name == "Test Tenant"
        assert tenant.slug == "test-tenant"
        assert tenant.is_active is True
        assert tenant.created_at is not None
        assert tenant.updated_at is not None

    async def test_tenant_slug_uniqueness(self, test_db: AsyncSession):
        """Test tenant slug uniqueness constraint"""
        tenant1 = Tenant(name="Tenant 1", slug="test-slug")
        tenant2 = Tenant(name="Tenant 2", slug="test-slug")
        test_db.add_all([tenant1, tenant2])

        with pytest.raises(Exception):  # IntegrityError expected
            await test_db.commit()


@pytest.mark.asyncio
@pytest.mark.unit
class TestRoleModel:
    """Test Role model functionality"""

    async def test_role_creation(self, test_db: AsyncSession):
        """Test role model creation"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()

        role = Role(
            tenant_id=tenant.id,
            name="Admin",
            description="Administrator role",
            permissions='["admin", "read"]'
        )
        test_db.add(role)
        await test_db.commit()
        await test_db.refresh(role)

        assert role.id is not None
        assert role.name == "Admin"
        assert role.description == "Administrator role"
        assert role.permissions == '["admin", "read"]'

    async def test_role_has_permission(self, test_db: AsyncSession):
        """Test role permission checking"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()

        role = Role(
            tenant_id=tenant.id,
            name="Admin",
            permissions='["admin", "read", "write"]'
        )
        test_db.add(role)
        await test_db.commit()

        assert role.has_permission("admin") is True
        assert role.has_permission("read") is True
        assert role.has_permission("write") is True
        assert role.has_permission("delete") is False

    async def test_role_add_permission(self, test_db: AsyncSession):
        """Test adding permission to role"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()

        role = Role(
            tenant_id=tenant.id,
            name="User",
            permissions='["read"]'
        )
        test_db.add(role)
        await test_db.commit()

        role.add_permission("write")
        await test_db.commit()

        assert role.has_permission("read") is True
        assert role.has_permission("write") is True

    async def test_role_remove_permission(self, test_db: AsyncSession):
        """Test removing permission from role"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()

        role = Role(
            tenant_id=tenant.id,
            name="User",
            permissions='["read", "write"]'
        )
        test_db.add(role)
        await test_db.commit()

        role.remove_permission("write")
        await test_db.commit()

        assert role.has_permission("read") is True
        assert role.has_permission("write") is False


@pytest.mark.asyncio
@pytest.mark.unit
class TestArticleModel:
    """Test Article model functionality"""

    async def test_article_creation(self, test_db: AsyncSession):
        """Test article model creation"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()

        user = User(
            tenant_id=tenant.id,
            email="author@example.com",
            hashed_password="hashed",
            first_name="Author",
            last_name="Test",
            full_name="Author Test"
        )
        test_db.add(user)
        await test_db.commit()

        article = Article(
            tenant_id=tenant.id,
            author_id=user.id,
            title="Test Article",
            slug="test-article",
            content="<p>Test content</p>",
            excerpt="Test excerpt",
            status="draft"
        )
        test_db.add(article)
        await test_db.commit()
        await test_db.refresh(article)

        assert article.id is not None
        assert article.title == "Test Article"
        assert article.slug == "test-article"
        assert article.status == "draft"
        assert article.view_count == 0
        assert article.created_at is not None
        assert article.updated_at is not None

    async def test_article_with_tags(self, test_db: AsyncSession):
        """Test article with tags"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()

        user = User(
            tenant_id=tenant.id,
            email="author@example.com",
            hashed_password="hashed",
            first_name="Author",
            last_name="Test",
            full_name="Author Test"
        )
        test_db.add(user)
        await test_db.commit()

        article = Article(
            tenant_id=tenant.id,
            author_id=user.id,
            title="Test Article",
            slug="test-article",
            content="<p>Test content</p>",
            tags=["tag1", "tag2", "tag3"]
        )
        test_db.add(article)
        await test_db.commit()
        await test_db.refresh(article)

        assert article.tags == ["tag1", "tag2", "tag3"]


@pytest.mark.asyncio
@pytest.mark.unit
class TestCategoryModel:
    """Test Category model functionality"""

    async def test_category_creation(self, test_db: AsyncSession):
        """Test category model creation"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()

        category = Category(
            tenant_id=tenant.id,
            name="Test Category",
            slug="test-category",
            description="Test description"
        )
        test_db.add(category)
        await test_db.commit()
        await test_db.refresh(category)

        assert category.id is not None
        assert category.name == "Test Category"
        assert category.slug == "test-category"
        assert category.parent_id is None
        assert category.get_full_path() == "Test Category"

    async def test_category_hierarchy(self, test_db: AsyncSession):
        """Test category hierarchy with parent-child relationships"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()

        parent = Category(
            tenant_id=tenant.id,
            name="Parent Category",
            slug="parent-category"
        )
        test_db.add(parent)
        await test_db.commit()

        child = Category(
            tenant_id=tenant.id,
            name="Child Category",
            slug="child-category",
            parent_id=parent.id
        )
        test_db.add(child)
        await test_db.commit()
        await test_db.refresh(child)

        assert child.parent_id == parent.id
        assert child.get_full_path() == "Parent Category > Child Category"


@pytest.mark.asyncio
@pytest.mark.unit
class TestCommentModel:
    """Test Comment model functionality"""

    async def test_comment_creation(self, test_db: AsyncSession):
        """Test comment model creation"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()

        user = User(
            tenant_id=tenant.id,
            email="author@example.com",
            hashed_password="hashed",
            first_name="Author",
            last_name="Test",
            full_name="Author Test"
        )
        test_db.add(user)
        await test_db.commit()

        article = Article(
            tenant_id=tenant.id,
            author_id=user.id,
            title="Test Article",
            slug="test-article",
            content="<p>Test content</p>"
        )
        test_db.add(article)
        await test_db.commit()

        comment = Comment(
            tenant_id=tenant.id,
            article_id=article.id,
            author_id=user.id,
            content="Test comment content"
        )
        test_db.add(comment)
        await test_db.commit()
        await test_db.refresh(comment)

        assert comment.id is not None
        assert comment.content == "Test comment content"
        assert comment.parent_id is None
        assert comment.get_thread_depth() == 0

    async def test_comment_threading(self, test_db: AsyncSession):
        """Test comment threading with replies"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()

        user = User(
            tenant_id=tenant.id,
            email="author@example.com",
            hashed_password="hashed",
            first_name="Author",
            last_name="Test",
            full_name="Author Test"
        )
        test_db.add(user)
        await test_db.commit()

        article = Article(
            tenant_id=tenant.id,
            author_id=user.id,
            title="Test Article",
            slug="test-article",
            content="<p>Test content</p>"
        )
        test_db.add(article)
        await test_db.commit()

        parent_comment = Comment(
            tenant_id=tenant.id,
            article_id=article.id,
            author_id=user.id,
            content="Parent comment"
        )
        test_db.add(parent_comment)
        await test_db.commit()

        reply_comment = Comment(
            tenant_id=tenant.id,
            article_id=article.id,
            author_id=user.id,
            content="Reply comment",
            parent_id=parent_comment.id
        )
        test_db.add(reply_comment)
        await test_db.commit()
        await test_db.refresh(reply_comment)

        assert reply_comment.parent_id == parent_comment.id
        assert reply_comment.get_thread_depth() == 1


@pytest.mark.asyncio
@pytest.mark.unit
class TestAuditLogModel:
    """Test AuditLog model functionality"""

    async def test_audit_log_creation(self, test_db: AsyncSession):
        """Test audit log model creation"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()

        audit_log = AuditLog(
            tenant_id=tenant.id,
            event_id=str(uuid4()),
            event_type="user_login",
            severity="low",
            resource="auth",
            action="login",
            status="success",
            description="User logged in",
            hash="dummy_hash"
        )
        test_db.add(audit_log)
        await test_db.commit()
        await test_db.refresh(audit_log)

        assert audit_log.id is not None
        assert audit_log.event_type == "user_login"
        assert audit_log.severity == "low"
        assert audit_log.status == "success"
        assert audit_log.created_at is not None


@pytest.mark.asyncio
@pytest.mark.unit
class TestRefreshTokenModel:
    """Test RefreshToken model functionality"""

    async def test_refresh_token_creation(self, test_db: AsyncSession):
        """Test refresh token model creation"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()

        user = User(
            tenant_id=tenant.id,
            email="user@example.com",
            hashed_password="hashed",
            first_name="Test",
            last_name="User",
            full_name="Test User"
        )
        test_db.add(user)
        await test_db.commit()

        refresh_token = RefreshToken(
            user_id=user.id,
            token="refresh_token_string",
            expires_at=datetime.now(timezone.utc)
        )
        test_db.add(refresh_token)
        await test_db.commit()
        await test_db.refresh(refresh_token)

        assert refresh_token.id is not None
        assert refresh_token.token == "refresh_token_string"
        assert refresh_token.is_revoked is False

    async def test_refresh_token_revoke(self, test_db: AsyncSession):
        """Test refresh token revocation"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()

        user = User(
            tenant_id=tenant.id,
            email="user@example.com",
            hashed_password="hashed",
            first_name="Test",
            last_name="User",
            full_name="Test User"
        )
        test_db.add(user)
        await test_db.commit()

        refresh_token = RefreshToken(
            user_id=user.id,
            token="refresh_token_string",
            expires_at=datetime.now(timezone.utc)
        )
        test_db.add(refresh_token)
        await test_db.commit()

        refresh_token.revoke()
        await test_db.commit()

        assert refresh_token.is_revoked is True
        assert refresh_token.revoked_at is not None


@pytest.mark.asyncio
@pytest.mark.unit
class TestSystemUserFlagModel:
    """Test SystemUserFlag model functionality"""

    async def test_system_user_flag_creation(self, test_db: AsyncSession):
        """Test system user flag model creation"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()

        user = User(
            tenant_id=tenant.id,
            email="user@example.com",
            hashed_password="hashed",
            first_name="Test",
            last_name="User",
            full_name="Test User"
        )
        test_db.add(user)
        await test_db.commit()

        flag = SystemUserFlag(
            user_id=user.id,
            flag_type="super_admin",
            is_active=True
        )
        test_db.add(flag)
        await test_db.commit()
        await test_db.refresh(flag)

        assert flag.id is not None
        assert flag.flag_type == "super_admin"
        assert flag.is_active is True
        assert flag.created_at is not None


@pytest.mark.asyncio
@pytest.mark.unit
class TestUserRoleModel:
    """Test UserRole model functionality"""

    async def test_user_role_creation(self, test_db: AsyncSession):
        """Test user role association model creation"""
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        test_db.add(tenant)
        await test_db.commit()

        user = User(
            tenant_id=tenant.id,
            email="user@example.com",
            hashed_password="hashed",
            first_name="Test",
            last_name="User",
            full_name="Test User"
        )
        test_db.add(user)

        role = Role(
            tenant_id=tenant.id,
            name="Admin",
            permissions='["admin"]'
        )
        test_db.add(role)
        await test_db.commit()

        user_role = UserRole(user_id=user.id, role_id=role.id)
        test_db.add(user_role)
        await test_db.commit()
        await test_db.refresh(user_role)

        assert user_role.user_id == user.id
        assert user_role.role_id == role.id
        assert user_role.assigned_at is not None