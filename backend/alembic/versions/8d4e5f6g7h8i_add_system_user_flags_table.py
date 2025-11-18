"""Add system_user_flags table

Revision ID: 8d4e5f6g7h8i
Revises: 7a3f8b9e2c1d
Create Date: 2025-11-18 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8d4e5f6g7h8i'
down_revision: Union[str, None] = '7a3f8b9e2c1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create system_user_flags table for database-driven system user identification.

    This table replaces hardcoded email lists with a secure, database-driven approach
    to identify system users (admins, demo users, etc.).

    Security improvements:
    - No hardcoded credentials in source code
    - Clear audit trail with timestamps
    - Configurable via migrations and management commands
    - Supports multiple user types
    """

    # Create system_user_flags table
    op.create_table(
        'system_user_flags',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('flag_type', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='fk_system_user_flags_user_id'),
        sa.PrimaryKeyConstraint('user_id', 'flag_type', name='pk_system_user_flags')
    )

    # Create index on user_id for faster lookups
    op.create_index('idx_system_user_flags_user_id', 'system_user_flags', ['user_id'])

    # Create index on flag_type for filtering
    op.create_index('idx_system_user_flags_flag_type', 'system_user_flags', ['flag_type'])


def downgrade() -> None:
    """
    Remove system_user_flags table and its indexes.
    """

    # Drop indexes
    op.drop_index('idx_system_user_flags_flag_type', table_name='system_user_flags')
    op.drop_index('idx_system_user_flags_user_id', table_name='system_user_flags')

    # Drop table
    op.drop_table('system_user_flags')
