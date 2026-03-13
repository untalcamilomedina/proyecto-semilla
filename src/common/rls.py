"""
PostgreSQL Row-Level Security (RLS) utilities.

Provides helpers to enable RLS on tenant-scoped tables and generate
security policies that restrict access based on the current tenant.

The middleware sets `app.tenant_id` via SET LOCAL on each request,
and RLS policies use this to filter rows automatically.
"""

from __future__ import annotations

from django.db import connection

# Tables that have an `organization_id` column pointing to multitenant_tenant
TENANT_SCOPED_TABLES = [
    # Core
    "core_permission",
    "core_role",
    "core_rolepermission",
    "core_membership",
    "core_roleauditlog",
    "core_onboardingstate",
    "core_activitylog",
    # Billing
    "billing_plan",
    "billing_price",
    "billing_subscription",
    "billing_invoice",
    # API
    "api_apikey",
    # CMS
    "cms_category",
    "cms_contentpage",
    "cms_mediaasset",
    # LMS
    "lms_course",
    "lms_section",
    "lms_lesson",
    "lms_enrollment",
    "lms_lessonprogress",
    "lms_certificate",
    "lms_review",
    # Community
    "community_space",
    "community_topic",
    "community_post",
    "community_reaction",
    "community_memberprofile",
    # MCP
    "mcp_mcpserver",
    "mcp_mcptool",
    "mcp_mcpresource",
    "mcp_mcpusagelog",
]

# Tables where the FK column is named differently
SPECIAL_FK_TABLES = {
    "core_onboardingstate": "tenant_id",
}


def get_fk_column(table_name: str) -> str:
    """Return the FK column name for a given table."""
    return SPECIAL_FK_TABLES.get(table_name, "organization_id")


def enable_rls_sql() -> list[str]:
    """Generate SQL statements to enable RLS on all tenant-scoped tables."""
    statements = []
    for table in TENANT_SCOPED_TABLES:
        fk_col = get_fk_column(table)
        statements.extend([
            f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;",
            f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;",
            # Policy: tenant isolation
            f"DROP POLICY IF EXISTS tenant_isolation ON {table};",
            f"""CREATE POLICY tenant_isolation ON {table}
                USING ({fk_col}::text = current_setting('app.tenant_id', true))
                WITH CHECK ({fk_col}::text = current_setting('app.tenant_id', true));""",
            # Policy: superuser bypass
            f"DROP POLICY IF EXISTS superuser_bypass ON {table};",
            f"""CREATE POLICY superuser_bypass ON {table}
                USING (current_setting('app.rls_bypass', true) = 'true');""",
        ])
    return statements


def disable_rls_sql() -> list[str]:
    """Generate SQL statements to disable RLS (for rollback)."""
    statements = []
    for table in TENANT_SCOPED_TABLES:
        statements.extend([
            f"DROP POLICY IF EXISTS tenant_isolation ON {table};",
            f"DROP POLICY IF EXISTS superuser_bypass ON {table};",
            f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;",
        ])
    return statements


def set_tenant_id(tenant_id: int | str) -> None:
    """Set the current tenant ID for RLS policy evaluation."""
    if connection.vendor != "postgresql":
        return
    with connection.cursor() as cursor:
        cursor.execute("SET LOCAL app.tenant_id = %s", [str(tenant_id)])


def set_rls_bypass(enabled: bool = True) -> None:
    """Enable/disable RLS bypass for superuser/admin operations."""
    if connection.vendor != "postgresql":
        return
    with connection.cursor() as cursor:
        cursor.execute(
            "SET LOCAL app.rls_bypass = %s",
            ["true" if enabled else "false"],
        )
