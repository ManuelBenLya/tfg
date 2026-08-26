from pydantic import BaseModel
from uuid import UUID

# -------------------------------------------------------------------
# 1. ESQUEMAS PARA EL REGISTRO PÚBLICO (NUEVA EMPRESA)
# -------------------------------------------------------------------
class RegistroEmpresaCreate(BaseModel):
    """
    Datos requeridos cuando un cliente nuevo registra su empresa 
    en la plataforma por primera vez.
    """
    nombre_empresa: str
    email: str
    password: str

# -------------------------------------------------------------------
# 2. ESQUEMAS PARA USUARIOS (EMPLEADOS)
# -------------------------------------------------------------------
class UsuarioBase(BaseModel):
    email: str
    rol: str = "usuario" # Por seguridad, por defecto nadie es admin

class UsuarioCreate(UsuarioBase):
    """
    Datos requeridos cuando un Administrador crea una cuenta 
    para un empleado de su equipo.
    """
    password: str

class UsuarioResponse(UsuarioBase):
    """
    Lo que devolvemos al frontend (oculta la contraseña, muestra IDs).
    """
    id: UUID
    empresa_id: UUID # 🌟 CRÍTICO: Para que Next.js sepa a qué empresa pertenece
    discord_webhook: str | None = None
    slack_webhook: str | None = None
    recibir_alertas_email: bool | None = True
    
    class Config:
        from_attributes = True

# -------------------------------------------------------------------
# 3. ESQUEMAS PARA AUTENTICACIÓN (JWT)
# -------------------------------------------------------------------
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