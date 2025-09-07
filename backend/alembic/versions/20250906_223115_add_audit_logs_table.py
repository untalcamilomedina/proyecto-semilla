"""Add audit_logs table

Revision ID: add_audit_logs
Revises: 9365aa3543ae
Create Date: 2025-09-07 03:29:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250906_223115'
down_revision: Union[str, None] = '20250905_095000'
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
        sa.Column('ip_address', sa.VARCHAR(length=45), autoincrement=False, nullable=True),
        sa.Column('user_agent', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('resource', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column('action', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.Column('status', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
        sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('metadata', sa.JSON(), autoincrement=False, nullable=True),
        sa.Column('tags', sa.JSON(), autoincrement=False, nullable=True),
        sa.Column('hash', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='audit_logs_pkey')
    )

    # Create indexes for better performance
    op.create_index('ix_audit_logs_event_id', 'audit_logs', ['event_id'], unique=False)
    op.create_index('ix_audit_logs_event_type', 'audit_logs', ['event_type'], unique=False)
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'], unique=False)
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'], unique=False)
    op.create_index('ix_audit_logs_tenant_id', 'audit_logs', ['tenant_id'], unique=False)
    op.create_index('ix_audit_logs_resource', 'audit_logs', ['resource'], unique=False)
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'], unique=False)
    op.create_index('ix_audit_logs_status', 'audit_logs', ['status'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_audit_logs_status', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_index('ix_audit_logs_resource', table_name='audit_logs')
    op.drop_index('ix_audit_logs_tenant_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_timestamp', table_name='audit_logs')
    op.drop_index('ix_audit_logs_event_type', table_name='audit_logs')
    op.drop_index('ix_audit_logs_event_id', table_name='audit_logs')

    # Drop table
    op.drop_table('audit_logs')