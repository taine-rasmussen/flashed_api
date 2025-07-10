"""drop grade column

Revision ID: e281b6943d2e
Revises: 24c568ef5481
Create Date: 2025-07-11 00:31:49.897460

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e281b6943d2e'
down_revision: Union[str, None] = '24c568ef5481'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
