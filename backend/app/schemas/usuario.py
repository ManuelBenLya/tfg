from pydantic import BaseModel
from uuid import UUID


class RegistroEmpresaCreate(BaseModel):
    """Datos para el alta de una nueva empresa y su administrador raíz."""
    nombre_empresa: str
    email: str
    password: str


class UsuarioBase(BaseModel):
    email: str
    rol: str = "usuario"

class UsuarioCreate(UsuarioBase):
    """Datos para la creación de un empleado por parte de un administrador."""
    password: str

class UsuarioResponse(UsuarioBase):
    """Esquema de respuesta al frontend; excluye la contraseña y expone los IDs."""
    id: UUID
    empresa_id: UUID
    discord_webhook: str | None = None
    slack_webhook: str | None = None
    recibir_alertas_email: bool | None = True
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None


class AjustesUpdate(BaseModel):
    discord_webhook: str | None = None
    slack_webhook: str | None = None
    recibir_alertas_email: bool | None = True


class EmpresaSMTPResponse(BaseModel):
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_user: str | None = None
    smtp_from: str | None = None
    has_password: bool = False

    class Config:
        from_attributes = True


class EmpresaSMTPUpdate(BaseModel):
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None