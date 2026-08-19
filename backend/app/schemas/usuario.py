from pydantic import BaseModel
from uuid import UUID

# 1. Esquema Base: Las propiedades que comparten todos los usuarios
class UsuarioBase(BaseModel):
    email: str
    rol: str = "administrador"

# 2. Esquema de Creación: Lo que pedimos cuando alguien se registra (añade la contraseña)
class UsuarioCreate(UsuarioBase):
    password: str

# 3. Esquema de Respuesta: Lo que devolvemos al frontend (oculta la contraseña, muestra el ID)
class UsuarioResponse(UsuarioBase):
    id: UUID
    
    # Configuración fundamental para que Pydantic entienda los modelos de SQLAlchemy
    class Config:
        from_attributes = True

# Si no lo tienes, asegúrate de importar BaseModel arriba:
# from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None