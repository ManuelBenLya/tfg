"""add_discos_json_column

Revision ID: 410a08883ccb
Revises: e5f9c9d937b2
Create Date: 2026-08-23 16:30:26.714935

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '410a08883ccb'
down_revision: Union[str, Sequence[str], None] = 'e5f9c9d937b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('metricas_hardware', sa.Column('discos_json', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('metricas_hardware', 'discos_json')
