"""Convertir metricas a hypertable

Revision ID: a550ef90868d
Revises: 89102f3615b7
Create Date: 2026-08-17 18:00:11.409445

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a550ef90868d'
down_revision: Union[str, Sequence[str], None] = '89102f3615b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convertimos la tabla estándar a hypertable particionada por la columna 'tiempo'
    op.execute("SELECT create_hypertable('metricas_hardware', 'tiempo');")

def downgrade() -> None:
    # Si hacemos un rollback, esto revierte la hypertable a una tabla normal
    op.execute("DROP EXTENSION IF EXISTS timescaledb CASCADE;")