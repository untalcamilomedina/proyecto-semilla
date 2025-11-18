"""Add Row Level Security policies

Revision ID: 7a3f8b9e2c1d
Revises: 4859d159e0c9
Create Date: 2025-11-18 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '7a3f8b9e2c1d'
down_revision: Union[str, None] = 'remove_cms'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Implements Row Level Security (RLS) for multi-tenant isolation.
    This migration creates helper functions, enables RLS on tables, and creates security policies.
    """

    # Create helper functions for RLS
    op.execute("""
        CREATE OR REPLACE FUNCTION current_tenant_id()
        RETURNS UUID AS $$
        BEGIN
            RETURN NULLIF(current_setting('app.current_tenant_id', TRUE), '')::UUID;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION is_super_admin()
        RETURNS BOOLEAN AS $$
        BEGIN
            RETURN COALESCE(current_setting('app.user_role', TRUE), '') = 'super_admin';
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION current_user_id()
        RETURNS UUID AS $$
        BEGIN
            RETURN NULLIF(current_setting('app.current_user_id', TRUE), '')::UUID;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)

    # Enable RLS on all tables
    op.execute("ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE roles ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY;")

    # ===========================================
    # TENANT POLICIES
    # ===========================================

    # Tenant isolation: Users can only see tenants they belong to or child tenants
    op.execute("""
        CREATE POLICY tenant_isolation_policy ON tenants
            FOR ALL
            USING (
                id = current_tenant_id() OR
                parent_tenant_id = current_tenant_id() OR
                is_super_admin()
            );
    """)

    # Tenant creation: Only super_admin can create root tenants
    op.execute("""
        CREATE POLICY tenant_creation_policy ON tenants
            FOR INSERT
            WITH CHECK (
                (parent_tenant_id IS NULL AND is_super_admin()) OR
                (parent_tenant_id = current_tenant_id())
            );
    """)

    # ===========================================
    # USER POLICIES
    # ===========================================

    # User isolation: Users can only see users from their tenant
    op.execute("""
        CREATE POLICY user_tenant_isolation_policy ON users
            FOR ALL
            USING (
                tenant_id = current_tenant_id() OR
                is_super_admin()
            );
    """)

    # User creation: Can only create users in current tenant
    op.execute("""
        CREATE POLICY user_creation_policy ON users
            FOR INSERT
            WITH CHECK (
                tenant_id = current_tenant_id() OR
                is_super_admin()
            );
    """)

    # User update: Only self or super_admin can update
    op.execute("""
        CREATE POLICY user_update_policy ON users
            FOR UPDATE
            USING (
                id = current_user_id() OR
                is_super_admin()
            )
            WITH CHECK (
                tenant_id = current_tenant_id() OR
                is_super_admin()
            );
    """)

    # Prevent tenant_id changes
    op.execute("""
        CREATE POLICY prevent_tenant_id_change ON users
            FOR UPDATE
            USING (tenant_id = current_tenant_id() OR is_super_admin())
            WITH CHECK (tenant_id = current_tenant_id() OR is_super_admin());
    """)

    # ===========================================
    # ROLE POLICIES
    # ===========================================

    # Role isolation: Roles only from current tenant
    op.execute("""
        CREATE POLICY role_tenant_isolation_policy ON roles
            FOR ALL
            USING (
                tenant_id = current_tenant_id() OR
                is_super_admin()
            );
    """)

    # Role creation: Only in current tenant
    op.execute("""
        CREATE POLICY role_creation_policy ON roles
            FOR INSERT
            WITH CHECK (
                tenant_id = current_tenant_id() OR
                is_super_admin()
            );
    """)

    # ===========================================
    # USER_ROLES POLICIES
    # ===========================================

    # User role isolation: Only roles from current tenant
    op.execute("""
        CREATE POLICY user_role_tenant_isolation_policy ON user_roles
            FOR ALL
            USING (
                EXISTS (
                    SELECT 1 FROM users u
                    WHERE u.id = user_roles.user_id
                    AND (u.tenant_id = current_tenant_id() OR is_super_admin())
                ) AND
                EXISTS (
                    SELECT 1 FROM roles r
                    WHERE r.id = user_roles.role_id
                    AND (r.tenant_id = current_tenant_id() OR is_super_admin())
                )
            );
    """)

    # User role creation: Only assign roles from current tenant
    op.execute("""
        CREATE POLICY user_role_creation_policy ON user_roles
            FOR INSERT
            WITH CHECK (
                EXISTS (
                    SELECT 1 FROM users u
                    WHERE u.id = user_roles.user_id
                    AND (u.tenant_id = current_tenant_id() OR is_super_admin())
                ) AND
                EXISTS (
                    SELECT 1 FROM roles r
                    WHERE r.id = user_roles.role_id
                    AND (r.tenant_id = current_tenant_id() OR is_super_admin())
                )
            );
    """)

    # Restrict super_admin role changes to super_admin only
    op.execute("""
        CREATE POLICY restrict_super_admin_role ON user_roles
            FOR ALL
            USING (
                NOT EXISTS (
                    SELECT 1 FROM roles r
                    WHERE r.id = user_roles.role_id
                    AND r.name = 'super_admin'
                ) OR is_super_admin()
            );
    """)

    # ===========================================
    # REFRESH_TOKENS POLICIES
    # ===========================================

    # Refresh token isolation: Only tokens from current tenant
    op.execute("""
        CREATE POLICY refresh_token_tenant_isolation_policy ON refresh_tokens
            FOR ALL
            USING (
                tenant_id = current_tenant_id() OR
                is_super_admin()
            );
    """)

    # Refresh token creation: Only in current tenant
    op.execute("""
        CREATE POLICY refresh_token_creation_policy ON refresh_tokens
            FOR INSERT
            WITH CHECK (
                tenant_id = current_tenant_id() OR
                is_super_admin()
            );
    """)


def downgrade() -> None:
    """
    Remove all RLS policies and helper functions.
    """

    # Drop all policies
    op.execute("DROP POLICY IF EXISTS refresh_token_creation_policy ON refresh_tokens;")
    op.execute("DROP POLICY IF EXISTS refresh_token_tenant_isolation_policy ON refresh_tokens;")
    op.execute("DROP POLICY IF EXISTS restrict_super_admin_role ON user_roles;")
    op.execute("DROP POLICY IF EXISTS user_role_creation_policy ON user_roles;")
    op.execute("DROP POLICY IF EXISTS user_role_tenant_isolation_policy ON user_roles;")
    op.execute("DROP POLICY IF EXISTS role_creation_policy ON roles;")
    op.execute("DROP POLICY IF EXISTS role_tenant_isolation_policy ON roles;")
    op.execute("DROP POLICY IF EXISTS prevent_tenant_id_change ON users;")
    op.execute("DROP POLICY IF EXISTS user_update_policy ON users;")
    op.execute("DROP POLICY IF EXISTS user_creation_policy ON users;")
    op.execute("DROP POLICY IF EXISTS user_tenant_isolation_policy ON users;")
    op.execute("DROP POLICY IF EXISTS tenant_creation_policy ON tenants;")
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON tenants;")

    # Disable RLS on all tables
    op.execute("ALTER TABLE refresh_tokens DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE user_roles DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE roles DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE tenants DISABLE ROW LEVEL SECURITY;")

    # Drop helper functions
    op.execute("DROP FUNCTION IF EXISTS current_user_id();")
    op.execute("DROP FUNCTION IF EXISTS is_super_admin();")
    op.execute("DROP FUNCTION IF EXISTS current_tenant_id();")
