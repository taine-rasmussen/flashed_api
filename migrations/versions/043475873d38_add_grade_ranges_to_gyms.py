"""add grade_ranges to gyms

Revision ID: 043475873d38
Revises: e281b6943d2e
Create Date: 2025-07-11 01:15:20.473677

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
revision: str = '043475873d38'
down_revision: Union[str, None] = 'e281b6943d2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        'gyms',
        sa.Column(
            'grade_ranges',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default='[]'
        )
    )
    op.alter_column('gyms', 'grade_ranges')


def downgrade() -> None:
    pass
