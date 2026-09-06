from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from app.schemas.usuario import UsuarioResponse

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
    
    usuarios_con_acceso: Optional[List[UsuarioResponse]] = []
    
    class Config:
        from_attributes = True

class UmbralesUpdate(BaseModel):
    umbral_cpu: float
    umbral_ram: float
    umbral_disco: float
    umbral_red: float


# Esquema para actualizar datos
class ServidorUpdate(BaseModel):
    nombre: str


# Esquema para asignación de usuarios a un servidor
class AsignarUsuariosRequest(BaseModel):
    usuario_ids: List[UUID]


# Esquema genérico de respuesta con mensaje
class MensajeResponse(BaseModel):
    mensaje: str