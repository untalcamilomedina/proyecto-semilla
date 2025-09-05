"""Add audit logs table for security and compliance

Revision ID: 20250905_075700
Revises: 20250904_190027
Create Date: 2025-09-05 07:57:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250905_075700'
down_revision: Union[str, None] = '20250904_190027'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('event_id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('event_type', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.Column('severity', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
        sa.Column('timestamp', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=True),
        sa.Column('tenant_id', sa.UUID(), autoincrement=False, nullable=True),
        sa.Column('session_id', sa.UUID(), autoincrement=False, nullable=True),
        sa.Column('ip_address', postgresql.INET(), autoincrement=False, nullable=True),
        sa.Column('user_agent', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('resource', sa.VARCHAR(length=500), autoincrement=False, nullable=True),
        sa.Column('action', sa.VARCHAR(length=10), autoincrement=False, nullable=True),
        sa.Column('status', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
        sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('metadata', postgresql.JSONB(), autoincrement=False, nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.VARCHAR(length=50)), autoincrement=False, nullable=True),
        sa.Column('hash', sa.VARCHAR(length=64), autoincrement=False, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='audit_logs_user_id_fkey'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='audit_logs_tenant_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='audit_logs_pkey')
    )

    # Create indexes for performance
    op.create_index('ix_audit_logs_event_id', 'audit_logs', ['event_id'], unique=True)
    op.create_index('ix_audit_logs_event_type', 'audit_logs', ['event_type'], unique=False)
    op.create_index('ix_audit_logs_severity', 'audit_logs', ['severity'], unique=False)
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'], unique=False)
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'], unique=False)
    op.create_index('ix_audit_logs_tenant_id', 'audit_logs', ['tenant_id'], unique=False)
    op.create_index('ix_audit_logs_status', 'audit_logs', ['status'], unique=False)

    # Create composite indexes for common queries
    op.create_index('idx_audit_logs_tenant_timestamp', 'audit_logs', ['tenant_id', 'timestamp'], unique=False)
    op.create_index('idx_audit_logs_user_timestamp', 'audit_logs', ['user_id', 'timestamp'], unique=False)
    op.create_index('idx_audit_logs_event_type_timestamp', 'audit_logs', ['event_type', 'timestamp'], unique=False)

    # Create partial index for failed events
    op.create_index('idx_audit_logs_failed_events', 'audit_logs', ['timestamp'], unique=False,
                   postgresql_where=sa.text("status != 'success'"))


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_audit_logs_failed_events', table_name='audit_logs')
    op.drop_index('idx_audit_logs_event_type_timestamp', table_name='audit_logs')
    op.drop_index('idx_audit_logs_user_timestamp', table_name='audit_logs')
    op.drop_index('idx_audit_logs_tenant_timestamp', table_name='audit_logs')
    op.drop_index('ix_audit_logs_status', table_name='audit_logs')
    op.drop_index('ix_audit_logs_tenant_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_timestamp', table_name='audit_logs')
    op.drop_index('ix_audit_logs_severity', table_name='audit_logs')
    op.drop_index('ix_audit_logs_event_type', table_name='audit_logs')
    op.drop_index('ix_audit_logs_event_id', table_name='audit_logs')

    # Drop table
    op.drop_table('audit_logs')