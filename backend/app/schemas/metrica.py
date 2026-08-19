from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class MetricaCreate(BaseModel):
    cpu_usage_pct: float
    ram_usage_mb: float
    disk_usage_pct: float
    network_latency_ms: float
    # El tiempo lo puede generar el agente en el servidor o lo calculamos aquí
    tiempo: datetime | None = None

class MetricaResponse(MetricaCreate):
    servidor_id: UUID
    tiempo: datetime

    class Config:
        from_attributes = True