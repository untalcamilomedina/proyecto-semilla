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
down_revision = '9365aa3543ae'
branch_labels = None
depends_on = None

def upgrade():
    """Add basic performance indexes for production optimization"""

    # Articles table - Basic indexes for tenant-based queries
    op.create_index('idx_articles_tenant_created', 'articles', ['tenant_id', 'created_at'])
    op.create_index('idx_articles_tenant_status', 'articles', ['tenant_id', 'status'])
    op.create_index('idx_articles_author_created', 'articles', ['author_id', 'created_at'])

    # Users table - Authentication and tenant isolation
    op.create_index('idx_users_email_tenant', 'users', ['email', 'tenant_id'])
    op.create_index('idx_users_tenant_role', 'users', ['tenant_id'])

    # Categories table - Basic indexes
    op.create_index('idx_categories_tenant', 'categories', ['tenant_id'])
    op.create_index('idx_categories_parent', 'categories', ['parent_id'])

    # Comments table - Basic indexes
    op.create_index('idx_comments_article', 'comments', ['article_id'])
    op.create_index('idx_comments_tenant', 'comments', ['tenant_id'])

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