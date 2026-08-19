from pydantic import BaseModel
from typing import Optional
from uuid import UUID

# 1. Propiedades comunes
class ServidorBase(BaseModel):
    nombre: str
    ip_direccion: str
    estado: str = "activo"

# 2. Esquema de creación (no pedimos el token porque lo generará el backend)
class ServidorCreate(ServidorBase):
    pass

# 3. Esquema de respuesta (incluye el ID y el Token que acabamos de generar)
class ServidorResponse(ServidorBase):
    id: UUID
    token_auth: str
    
    umbral_cpu: Optional[float] = 90.0
    umbral_ram: Optional[float] = 16000.0
    umbral_disco: Optional[float] = 90.0
    umbral_red: Optional[float] = 500.0
    
    class Config:
        from_attributes = True

class UmbralesUpdate(BaseModel):
    umbral_cpu: float
    umbral_ram: float
    umbral_disco: float
    umbral_red: float