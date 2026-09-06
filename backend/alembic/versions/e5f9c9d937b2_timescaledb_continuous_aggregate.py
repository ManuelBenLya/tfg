"""timescaledb_continuous_aggregate

Revision ID: e5f9c9d937b2
Revises: d4e9b9c926a1
Create Date: 2026-08-23 17:52:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f9c9d937b2'
down_revision: Union[str, Sequence[str], None] = 'd4e9b9c926a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def check_timescale(connection) -> bool:
    res = connection.execute(sa.text("SELECT 1 FROM pg_extension WHERE extname = 'timescaledb';")).fetchone()
    if res:
        return True
    return False


def upgrade() -> None:
    connection = op.get_bind()
    is_timescale = check_timescale(connection)
    
    # Use autocommit_block to run the TimescaleDB DDL outside of transaction
    with op.get_context().autocommit_block():
        if is_timescale:
            # Creamos la vista materializada para agrupar métricas por servidor y por hora
            op.execute(sa.text("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS metricas_promedio_1h
                WITH (timescaledb.continuous) AS
                SELECT 
                    servidor_id,
                    time_bucket('1 hour', tiempo) AS bucket,
                    AVG(cpu_usage_pct) AS cpu_avg,
                    AVG(ram_usage_mb) AS ram_avg,
                    AVG(disk_usage_pct) AS disco_avg
                FROM metricas_hardware
                GROUP BY servidor_id, bucket;
            """))

            # Configuramos la política de actualización automática para TimescaleDB
            op.execute(sa.text("""
                SELECT add_continuous_aggregate_policy('metricas_promedio_1h',
                    start_offset => INTERVAL '3 days',
                    end_offset => INTERVAL '1 hour',
                    schedule_interval => INTERVAL '1 hour');
            """))
        else:
            print("TimescaleDB no está disponible. Creando 'metricas_promedio_1h' como vista estándar de PostgreSQL.")
            op.execute(sa.text("""
                CREATE OR REPLACE VIEW metricas_promedio_1h AS
                SELECT 
                    servidor_id,
                    date_trunc('hour', tiempo) AS bucket,
                    AVG(cpu_usage_pct) AS cpu_avg,
                    AVG(ram_usage_mb) AS ram_avg,
                    AVG(disk_usage_pct) AS disco_avg
                FROM metricas_hardware
                GROUP BY servidor_id, bucket;
            """))


def downgrade() -> None:
    connection = op.get_bind()
    is_timescale = check_timescale(connection)
    
    with op.get_context().autocommit_block():
        if is_timescale:
            # Eliminamos la vista materializada (y su política asociada por cascada)
            op.execute(sa.text("DROP MATERIALIZED VIEW IF EXISTS metricas_promedio_1h CASCADE;"))
        else:
            # Eliminamos la vista estándar
            op.execute(sa.text("DROP VIEW IF EXISTS metricas_promedio_1h CASCADE;"))
