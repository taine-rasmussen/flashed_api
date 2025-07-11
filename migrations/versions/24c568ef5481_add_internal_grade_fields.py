"""Add internal grade fields

Revision ID: 24c568ef5481
Revises: 5a39b0ee03c2
Create Date: 2025-07-11 00:18:59.798994
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '24c568ef5481'
down_revision: Union[str, None] = '5a39b0ee03c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('climbs', 'internal_grade',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)
    op.alter_column('climbs', 'original_grade',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
    op.alter_column('climbs', 'original_scale',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
    op.create_index(op.f('ix_climbs_internal_grade'), 'climbs', ['internal_grade'], unique=False)

    op.execute("ALTER TABLE climbs DROP COLUMN IF EXISTS grade;")





def downgrade() -> None:
    # Recreate old grade column if rolling back
    op.add_column('climbs', sa.Column('grade', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_climbs_internal_grade'), table_name='climbs')
    op.create_index('ix_climbs_grade', 'climbs', ['grade'], unique=False)

    # Make new fields nullable again on rollback
    op.alter_column('climbs', 'original_scale',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
    op.alter_column('climbs', 'original_grade',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
    op.alter_column('climbs', 'internal_grade',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)
