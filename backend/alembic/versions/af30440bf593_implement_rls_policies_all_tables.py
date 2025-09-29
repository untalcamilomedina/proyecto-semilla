"""implement_rls_policies_all_tables

Revision ID: af30440bf593
Revises: d8e319c83391
Create Date: 2025-09-29 17:45:26.612103

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af30440bf593'
down_revision: Union[str, None] = 'd8e319c83391'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Implement Row Level Security (RLS) policies for all multi-tenant tables
    This ensures complete data isolation between tenants
    """
    
    # Create RLS helper functions if they don't exist
    op.execute("""
        CREATE OR REPLACE FUNCTION current_tenant_id()
        RETURNS UUID AS $$
        BEGIN
            RETURN current_setting('app.current_tenant_id')::UUID;
        EXCEPTION
            WHEN undefined_object THEN
                RAISE EXCEPTION 'Tenant context not set. Use SET LOCAL app.current_tenant_id = ''your-tenant-id'';';
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)
    
    op.execute("""
        CREATE OR REPLACE FUNCTION user_belongs_to_current_tenant(user_tenant_id UUID)
        RETURNS BOOLEAN AS $$
        BEGIN
            RETURN user_tenant_id = current_tenant_id();
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)
    
    # Enable RLS on all multi-tenant tables
    tables_with_rls = [
        'users',
        'roles', 
        'user_roles',
        'refresh_tokens',
        'audit_log',
        'system_user_flag',
        'modules',
        'module_configurations',
        'module_versions',
        'analytics_events',
        'analytics_metrics', 
        'analytics_dashboards',
        'analytics_reports',
        'module_reviews',
        'module_ratings',
        'module_downloads',
        'module_updates',
        'module_licenses'
    ]
    
    for table in tables_with_rls:
        # Enable RLS
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        
        # Create tenant isolation policy
        op.execute(f"""
            CREATE POLICY tenant_isolation_policy ON {table}
            FOR ALL USING (tenant_id = current_tenant_id());
        """)
        
        print(f"✅ RLS enabled for table: {table}")
    
    # Special handling for tables without tenant_id but with user_id
    user_tables = [
        'module_marketplace_entries'  # This table doesn't have tenant_id but has publisher_id (user_id)
    ]
    
    for table in user_tables:
        # Enable RLS
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        
        # Create policy based on user's tenant (for marketplace entries)
        op.execute(f"""
            CREATE POLICY user_tenant_isolation_policy ON {table}
            FOR ALL USING (
                publisher_id IN (
                    SELECT id FROM users WHERE tenant_id = current_tenant_id()
                )
            );
        """)
        
        print(f"✅ RLS enabled for user-based table: {table}")
    
    # Special handling for module_categories (global table, no RLS needed)
    # module_registry is also global, no RLS needed
    
    print("🎉 RLS implementation completed for all multi-tenant tables!")


def downgrade() -> None:
    """
    Remove RLS policies and functions
    """
    
    # Drop policies for all tables
    tables_with_rls = [
        'users',
        'roles', 
        'user_roles',
        'refresh_tokens',
        'audit_log',
        'system_user_flag',
        'modules',
        'module_configurations',
        'module_versions',
        'analytics_events',
        'analytics_metrics', 
        'analytics_dashboards',
        'analytics_reports',
        'module_reviews',
        'module_ratings',
        'module_downloads',
        'module_updates',
        'module_licenses',
        'module_marketplace_entries'
    ]
    
    for table in tables_with_rls:
        try:
            op.execute(f"DROP POLICY IF EXISTS tenant_isolation_policy ON {table};")
            op.execute(f"DROP POLICY IF EXISTS user_tenant_isolation_policy ON {table};")
            op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")
            print(f"✅ RLS disabled for table: {table}")
        except Exception as e:
            print(f"⚠️  Warning: Could not disable RLS for {table}: {e}")
    
    # Drop helper functions
    try:
        op.execute("DROP FUNCTION IF EXISTS user_belongs_to_current_tenant(UUID);")
        op.execute("DROP FUNCTION IF EXISTS current_tenant_id();")
        print("✅ RLS helper functions removed")
    except Exception as e:
        print(f"⚠️  Warning: Could not remove RLS functions: {e}")
