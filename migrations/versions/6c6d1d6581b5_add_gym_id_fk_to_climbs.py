"""add gym_id FK to climbs

Revision ID: 6c6d1d6581b5
Revises: 043475873d38
Create Date: 2025-07-11 11:05:31.525002

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c6d1d6581b5'
down_revision: Union[str, None] = '043475873d38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        'climbs',
        sa.Column('gym_id', sa.Integer(), sa.ForeignKey('gyms.id'), nullable=True)
    )


def downgrade() -> None:
    pass
