from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class MetricaCreate(BaseModel):
    cpu_usage_pct: float
    ram_usage_mb: float
    disk_usage_pct: float
    disk_os_gb: Optional[float] = 0.0
    disk_db_gb: Optional[float] = 0.0
    disk_logs_gb: Optional[float] = 0.0
    disk_free_gb: Optional[float] = 0.0
    network_latency_ms: float
    discos_json: Optional[list] = None
    # El tiempo lo puede generar el agente en el servidor o lo calculamos aquí
    tiempo: datetime | None = None

class MetricaResponse(MetricaCreate):
    servidor_id: UUID
    tiempo: datetime

    class Config:
        from_attributes = True