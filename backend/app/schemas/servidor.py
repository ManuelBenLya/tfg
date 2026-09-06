from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from app.schemas.usuario import UsuarioResponse


class ServidorBase(BaseModel):
    nombre: str
    ip_direccion: str
    estado: str = "activo"

class ServidorCreate(ServidorBase):
    """Esquema de creación; el token se genera automáticamente en el backend."""
    pass

class ServidorResponse(ServidorBase):
    """Esquema de respuesta que incluye el ID, token y umbrales configurados."""
    id: UUID
    token_auth: str
    
    umbral_cpu: Optional[float] = 90.0
    umbral_ram: Optional[float] = 16000.0
    umbral_disco: Optional[float] = 90.0
    umbral_red: Optional[float] = 500.0
    
    usuarios_con_acceso: Optional[List[UsuarioResponse]] = []
    
    class Config:
        from_attributes = True

class UmbralesUpdate(BaseModel):
    umbral_cpu: float
    umbral_ram: float
    umbral_disco: float
    umbral_red: float

class ServidorUpdate(BaseModel):
    nombre: str

class AsignarUsuariosRequest(BaseModel):
    usuario_ids: List[UUID]

class MensajeResponse(BaseModel):
    mensaje: str