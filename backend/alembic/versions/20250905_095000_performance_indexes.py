"""Performance indexes for production optimization

Revision ID: 20250905_095000
Revises: 20250905_075700
Create Date: 2025-09-05 16:49:15.000000

Performance optimization indexes for enterprise production deployment.
Implements strategic indexing for critical query patterns and N+1 prevention.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '20250905_095000'
down_revision = '20250905_075700'
branch_labels = None
depends_on = None

def upgrade():
    """Add performance indexes for production optimization"""

    # Articles table - Most critical indexes for tenant-based queries
    op.create_index(
        'idx_articles_tenant_created',
        'articles',
        ['tenant_id', 'created_at'],
        postgresql_where=sa.text('deleted_at IS NULL'),
        postgresql_concurrently=True
    )

    op.create_index(
        'idx_articles_tenant_status',
        'articles',
        ['tenant_id', 'status'],
        postgresql_where=sa.text('deleted_at IS NULL'),
        postgresql_concurrently=True
    )

    op.create_index(
        'idx_articles_author_created',
        'articles',
        ['author_id', 'created_at'],
        postgresql_concurrently=True
    )

    # Users table - Authentication and tenant isolation
    op.create_index(
        'idx_users_email_tenant',
        'users',
        ['email', 'tenant_id'],
        postgresql_where=sa.text('active = true'),
        postgresql_concurrently=True
    )

    op.create_index(
        'idx_users_tenant_role',
        'users',
        ['tenant_id', 'role'],
        postgresql_where=sa.text('active = true'),
        postgresql_concurrently=True
    )

    # Audit logs - Performance for compliance queries
    op.create_index(
        'idx_audit_logs_tenant_timestamp',
        'audit_logs',
        ['tenant_id', 'timestamp'],
        postgresql_concurrently=True
    )

    op.create_index(
        'idx_audit_logs_event_type',
        'audit_logs',
        ['event_type', 'timestamp'],
        postgresql_concurrently=True
    )

    # Sessions - Performance for authentication
    op.create_index(
        'idx_sessions_user_expires',
        'sessions',
        ['user_id', 'expires_at'],
        postgresql_where=sa.text('expires_at > CURRENT_TIMESTAMP'),
        postgresql_concurrently=True
    )

    # Rate limiting - Performance for security
    op.create_index(
        'idx_rate_limits_key_window',
        'rate_limits',
        ['key', 'window_start'],
        postgresql_concurrently=True
    )

    # Metrics - Performance for monitoring
    op.create_index(
        'idx_metrics_tenant_timestamp',
        'metrics',
        ['tenant_id', 'timestamp'],
        postgresql_concurrently=True
    )

    op.create_index(
        'idx_metrics_type_timestamp',
        'metrics',
        ['metric_type', 'timestamp'],
        postgresql_concurrently=True
    )

    # Composite indexes for complex queries
    op.create_index(
        'idx_articles_composite_search',
        'articles',
        ['tenant_id', 'status', 'created_at', 'title'],
        postgresql_where=sa.text('deleted_at IS NULL'),
        postgresql_concurrently=True
    )

    # Partial indexes for active records only
    op.create_index(
        'idx_users_active_only',
        'users',
        ['tenant_id', 'last_login'],
        postgresql_where=sa.text('active = true AND deleted_at IS NULL'),
        postgresql_concurrently=True
    )

def downgrade():
    """Remove performance indexes"""

    # Remove all indexes in reverse order
    op.drop_index('idx_users_active_only', table_name='users')
    op.drop_index('idx_articles_composite_search', table_name='articles')
    op.drop_index('idx_metrics_type_timestamp', table_name='metrics')
    op.drop_index('idx_metrics_tenant_timestamp', table_name='metrics')
    op.drop_index('idx_rate_limits_key_window', table_name='rate_limits')
    op.drop_index('idx_sessions_user_expires', table_name='sessions')
    op.drop_index('idx_audit_logs_event_type', table_name='audit_logs')
    op.drop_index('idx_audit_logs_tenant_timestamp', table_name='audit_logs')
    op.drop_index('idx_users_tenant_role', table_name='users')
    op.drop_index('idx_users_email_tenant', table_name='users')
    op.drop_index('idx_articles_author_created', table_name='articles')
    op.drop_index('idx_articles_tenant_status', table_name='articles')
    op.drop_index('idx_articles_tenant_created', table_name='articles')