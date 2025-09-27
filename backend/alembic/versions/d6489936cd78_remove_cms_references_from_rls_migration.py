"""remove_cms_references_from_rls_migration

Revision ID: d6489936cd78
Revises: c1a145217280
Create Date: 2025-09-26 21:42:37.499204

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6489936cd78'
down_revision: Union[str, None] = 'c1a145217280'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove CMS table references from RLS migration
    # Drop policies for CMS tables that no longer exist
    op.execute("DROP POLICY IF EXISTS articles_tenant_isolation_policy ON articles;")
    op.execute("DROP POLICY IF EXISTS categories_tenant_isolation_policy ON categories;")
    op.execute("DROP POLICY IF EXISTS comments_tenant_isolation_policy ON comments;")
    op.execute("DROP POLICY IF EXISTS super_admin_bypass_policy ON articles;")
    op.execute("DROP POLICY IF EXISTS super_admin_bypass_policy ON categories;")
    op.execute("DROP POLICY IF EXISTS super_admin_bypass_policy ON comments;")
    
    # Disable RLS on CMS tables that no longer exist
    op.execute("ALTER TABLE articles DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE categories DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE comments DISABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    # Re-enable RLS on CMS tables (if they exist)
    op.execute("ALTER TABLE articles ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE categories ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE comments ENABLE ROW LEVEL SECURITY;")
    
    # Recreate policies for CMS tables
    op.execute("""
        CREATE POLICY articles_tenant_isolation_policy ON articles
        FOR ALL USING (tenant_id = current_tenant_id());
    """)
    op.execute("""
        CREATE POLICY categories_tenant_isolation_policy ON categories
        FOR ALL USING (tenant_id = current_tenant_id());
    """)
    op.execute("""
        CREATE POLICY comments_tenant_isolation_policy ON comments
        FOR ALL USING (tenant_id = current_tenant_id());
    """)
    op.execute("""
        CREATE POLICY super_admin_bypass_policy ON articles
        FOR ALL USING (
            current_setting('app.super_admin', true) = 'true'
        );
    """)
    op.execute("""
        CREATE POLICY super_admin_bypass_policy ON categories
        FOR ALL USING (
            current_setting('app.super_admin', true) = 'true'
        );
    """)
    op.execute("""
        CREATE POLICY super_admin_bypass_policy ON comments
        FOR ALL USING (
            current_setting('app.super_admin', true) = 'true'
        );
    """)
