"""merge_cms_removal_branches

Revision ID: c1a145217280
Revises: 899172c6bc74, 9365aa3543ae
Create Date: 2025-09-26 21:40:59.135192

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1a145217280'
down_revision: Union[str, None] = ('899172c6bc74', '9365aa3543ae')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
