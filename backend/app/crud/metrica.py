from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.models import MetricaHardware
from app.schemas.metrica import MetricaCreate

def create_metrica(db: Session, metrica: MetricaCreate, servidor_id: str):
    """
    Inserta una nueva lectura de hardware en la base de datos de series temporales.
    """
    # Si el agente no envía la hora exacta, le asignamos la del servidor backend en UTC
    tiempo_actual = metrica.tiempo if metrica.tiempo else datetime.now(timezone.utc)
    
    db_metrica = MetricaHardware(
        tiempo=tiempo_actual,
        servidor_id=servidor_id,
        cpu_usage_pct=metrica.cpu_usage_pct,
        ram_usage_mb=metrica.ram_usage_mb,
        disk_usage_pct=metrica.disk_usage_pct,
        network_latency_ms=metrica.network_latency_ms,
        disk_os_gb=metrica.disk_os_gb,
        disk_db_gb=metrica.disk_db_gb,
        disk_logs_gb=metrica.disk_logs_gb,
        disk_free_gb=metrica.disk_free_gb
    )
    
    db.add(db_metrica)
    db.commit()
    
    return db_metrica


def get_metricas_por_servidor(db: Session, servidor_id: str, limit: int = 50):
    """
    Extrae el historial reciente de métricas de un servidor específico,
    ordenado desde el dato más actual hacia atrás.
    """
    return db.query(MetricaHardware)\
             .filter(MetricaHardware.servidor_id == servidor_id)\
             .order_by(MetricaHardware.tiempo.desc())\
             .limit(limit)\
             .all()