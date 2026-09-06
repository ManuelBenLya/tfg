"""configure_timescaledb

Revision ID: d4e9b9c926a1
Revises: c4395b4e9223
Create Date: 2026-08-23 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e9b9c926a1'
down_revision: Union[str, Sequence[str], None] = 'c4395b4e9223'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def check_timescale(connection) -> bool:
    res = connection.execute(sa.text("SELECT 1 FROM pg_extension WHERE extname = 'timescaledb';")).fetchone()
    if res:
        return True
    res_avail = connection.execute(sa.text("SELECT 1 FROM pg_available_extensions WHERE name = 'timescaledb';")).fetchone()
    if res_avail:
        try:
            connection.execute(sa.text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"));
            return True
        except Exception:
            pass
    return False


def upgrade() -> None:
    connection = op.get_bind()
    if check_timescale(connection):
        # Convertir la tabla metricas_hardware a hypertable usando la columna 'tiempo'
        op.execute(sa.text("SELECT create_hypertable('metricas_hardware', 'tiempo', if_not_exists => TRUE);"))
    else:
        print("TimescaleDB no está disponible. Manteniendo 'metricas_hardware' como tabla estándar.")


def downgrade() -> None:
    pass
