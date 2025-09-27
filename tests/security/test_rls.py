"""
Tests for Row Level Security (RLS) implementation
Validates multi-tenant data isolation
"""

import pytest
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, set_tenant_context, create_rls_functions
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.system_user_flag import SystemUserFlag
from app.models.audit_log import AuditLog


@pytest.mark.asyncio
class TestRLS:
    """Test Row Level Security implementation"""

    async def test_current_tenant_id_function(self, db_session: AsyncSession):
        """Test that current_tenant_id() function works correctly"""
        # Set tenant context
        test_tenant_id = str(uuid4())
        set_tenant_context(test_tenant_id)

        # Test the function
        result = await db_session.execute(text("SELECT current_tenant_id()"))
        current_id = result.scalar()

        assert str(current_id) == test_tenant_id

    async def test_tenant_isolation_users(self, db_session: AsyncSession):
        """Test that users can only see data from their own tenant"""
        # Create two tenants
        tenant1 = Tenant(name="Tenant 1", slug="tenant1")
        tenant2 = Tenant(name="Tenant 2", slug="tenant2")
        db_session.add_all([tenant1, tenant2])
        await db_session.commit()

        # Create users for each tenant
        user1 = User(
            tenant_id=tenant1.id,
            email="user1@tenant1.com",
            hashed_password="hashed",
            first_name="User",
            last_name="One",
            full_name="User One"
        )
        user2 = User(
            tenant_id=tenant2.id,
            email="user2@tenant2.com",
            hashed_password="hashed",
            first_name="User",
            last_name="Two",
            full_name="User Two"
        )
        db_session.add_all([user1, user2])
        await db_session.commit()

        # Test tenant 1 context
        set_tenant_context(str(tenant1.id))
        result = await db_session.execute(text("SELECT COUNT(*) FROM users"))
        count_tenant1 = result.scalar()
        assert count_tenant1 == 1

        # Verify the user returned is from tenant1
        result = await db_session.execute(text("SELECT email FROM users"))
        emails = [row[0] for row in result.fetchall()]
        assert "user1@tenant1.com" in emails
        assert "user2@tenant2.com" not in emails

        # Test tenant 2 context
        set_tenant_context(str(tenant2.id))
        result = await db_session.execute(text("SELECT COUNT(*) FROM users"))
        count_tenant2 = result.scalar()
        assert count_tenant2 == 1

        # Verify the user returned is from tenant2
        result = await db_session.execute(text("SELECT email FROM users"))
        emails = [row[0] for row in result.fetchall()]
        assert "user2@tenant2.com" in emails
        assert "user1@tenant1.com" not in emails

    async def test_tenant_isolation_roles(self, db_session: AsyncSession):
        """Test that roles are properly isolated by tenant"""
        # Create two tenants
        tenant1 = Tenant(name="Tenant 1", slug="tenant1")
        tenant2 = Tenant(name="Tenant 2", slug="tenant2")
        db_session.add_all([tenant1, tenant2])
        await db_session.commit()

        # Create roles for each tenant
        role1 = Role(
            tenant_id=tenant1.id,
            name="Admin",
            description="Administrator role",
            permissions='["admin"]'
        )
        role2 = Role(
            tenant_id=tenant2.id,
            name="User",
            description="User role",
            permissions='["read"]'
        )
        db_session.add_all([role1, role2])
        await db_session.commit()

        # Test tenant 1 context
        set_tenant_context(str(tenant1.id))
        result = await db_session.execute(text("SELECT COUNT(*) FROM roles"))
        count_tenant1 = result.scalar()
        assert count_tenant1 == 1

        result = await db_session.execute(text("SELECT name FROM roles"))
        names = [row[0] for row in result.fetchall()]
        assert "Admin" in names
        assert "User" not in names

        # Test tenant 2 context
        set_tenant_context(str(tenant2.id))
        result = await db_session.execute(text("SELECT COUNT(*) FROM roles"))
        count_tenant2 = result.scalar()
        assert count_tenant2 == 1

        result = await db_session.execute(text("SELECT name FROM roles"))
        names = [row[0] for row in result.fetchall()]
        assert "User" in names
        assert "Admin" not in names

    async def test_tenant_isolation_user_roles(self, db_session: AsyncSession):
        """Test that user_roles are properly isolated by tenant"""
        # Create tenants and users
        tenant1 = Tenant(name="Tenant 1", slug="tenant1")
        tenant2 = Tenant(name="Tenant 2", slug="tenant2")
        db_session.add_all([tenant1, tenant2])
        await db_session.commit()

        user1 = User(
            tenant_id=tenant1.id,
            email="user1@tenant1.com",
            hashed_password="hashed",
            first_name="User",
            last_name="One",
            full_name="User One"
        )
        user2 = User(
            tenant_id=tenant2.id,
            email="user2@tenant2.com",
            hashed_password="hashed",
            first_name="User",
            last_name="Two",
            full_name="User Two"
        )
        db_session.add_all([user1, user2])
        await db_session.commit()

        # Create roles
        role1 = Role(
            tenant_id=tenant1.id,
            name="Admin",
            permissions='["admin"]'
        )
        role2 = Role(
            tenant_id=tenant2.id,
            name="User",
            permissions='["read"]'
        )
        db_session.add_all([role1, role2])
        await db_session.commit()

        # Create user_role associations
        user_role1 = UserRole(
            tenant_id=tenant1.id,
            user_id=user1.id,
            role_id=role1.id
        )
        user_role2 = UserRole(
            tenant_id=tenant2.id,
            user_id=user2.id,
            role_id=role2.id
        )
        db_session.add_all([user_role1, user_role2])
        await db_session.commit()

        # Test tenant 1 context
        set_tenant_context(str(tenant1.id))
        result = await db_session.execute(text("SELECT COUNT(*) FROM user_roles"))
        count_tenant1 = result.scalar()
        assert count_tenant1 == 1

        # Test tenant 2 context
        set_tenant_context(str(tenant2.id))
        result = await db_session.execute(text("SELECT COUNT(*) FROM user_roles"))
        count_tenant2 = result.scalar()
        assert count_tenant2 == 1

    async def test_tenant_isolation_audit_logs(self, db_session: AsyncSession):
        """Test that audit_logs are properly isolated by tenant"""
        # Create two tenants
        tenant1 = Tenant(name="Tenant 1", slug="tenant1")
        tenant2 = Tenant(name="Tenant 2", slug="tenant2")
        db_session.add_all([tenant1, tenant2])
        await db_session.commit()

        # Create audit logs for each tenant
        audit1 = AuditLog(
            tenant_id=tenant1.id,
            event_id=str(uuid4()),
            event_type="user_login",
            severity="low",
            user_id=None,
            resource="auth",
            action="login",
            status="success",
            description="User logged in",
            hash="dummy_hash"
        )
        audit2 = AuditLog(
            tenant_id=tenant2.id,
            event_id=str(uuid4()),
            event_type="user_logout",
            severity="low",
            user_id=None,
            resource="auth",
            action="logout",
            status="success",
            description="User logged out",
            hash="dummy_hash"
        )
        db_session.add_all([audit1, audit2])
        await db_session.commit()

        # Test tenant 1 context
        set_tenant_context(str(tenant1.id))
        result = await db_session.execute(text("SELECT COUNT(*) FROM audit_logs"))
        count_tenant1 = result.scalar()
        assert count_tenant1 == 1

        result = await db_session.execute(text("SELECT event_type FROM audit_logs"))
        events = [row[0] for row in result.fetchall()]
        assert "user_login" in events
        assert "user_logout" not in events

        # Test tenant 2 context
        set_tenant_context(str(tenant2.id))
        result = await db_session.execute(text("SELECT COUNT(*) FROM audit_logs"))
        count_tenant2 = result.scalar()
        assert count_tenant2 == 1

        result = await db_session.execute(text("SELECT event_type FROM audit_logs"))
        events = [row[0] for row in result.fetchall()]
        assert "user_logout" in events
        assert "user_login" not in events

    async def test_no_tenant_context_raises_error(self, db_session: AsyncSession):
        """Test that accessing data without tenant context raises an error"""
        # Clear tenant context
        set_tenant_context(None)

        # Try to access users table - should raise an error
        with pytest.raises(Exception):  # Should raise an exception due to RLS
            result = await db_session.execute(text("SELECT COUNT(*) FROM users"))
            result.scalar()

    async def test_super_admin_bypass(self, db_session: AsyncSession):
        """Test that super admin can bypass RLS"""
        # Create two tenants
        tenant1 = Tenant(name="Tenant 1", slug="tenant1")
        tenant2 = Tenant(name="Tenant 2", slug="tenant2")
        db_session.add_all([tenant1, tenant2])
        await db_session.commit()

        # Create users for each tenant
        user1 = User(
            tenant_id=tenant1.id,
            email="user1@tenant1.com",
            hashed_password="hashed",
            first_name="User",
            last_name="One",
            full_name="User One"
        )
        user2 = User(
            tenant_id=tenant2.id,
            email="user2@tenant2.com",
            hashed_password="hashed",
            first_name="User",
            last_name="Two",
            full_name="User Two"
        )
        db_session.add_all([user1, user2])
        await db_session.commit()

        # Set super admin context
        await db_session.execute(text("SET LOCAL app.super_admin = 'true'"))

        # Should be able to see all users regardless of tenant
        result = await db_session.execute(text("SELECT COUNT(*) FROM users"))
        total_count = result.scalar()
        assert total_count == 2

        # Clean up
        await db_session.execute(text("SET LOCAL app.super_admin = 'false'"))