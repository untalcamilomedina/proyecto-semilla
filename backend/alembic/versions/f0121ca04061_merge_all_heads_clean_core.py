"""merge_all_heads_clean_core

Revision ID: f0121ca04061
Revises: 20250920215932, 2bd316786238, 526579bd2552
Create Date: 2025-09-26 21:52:21.349341

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0121ca04061'
down_revision: Union[str, None] = ('20250920215932', '2bd316786238', '526579bd2552')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
