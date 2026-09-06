from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import os

from app.db.database import get_db, SessionLocal
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, Token, RegistroEmpresaCreate, AjustesUpdate, EmpresaSMTPResponse, EmpresaSMTPUpdate
from app.crud import usuario as crud_usuario
from app.core.config import settings
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import get_password_hash 
from app.api.deps import get_current_user, require_admin
from app.models.models import Usuario, Empresa
from app.models.enums import RolUsuario
from typing import List

router = APIRouter()
MASTER_SECRET_KEY = settings.MASTER_SECRET_KEY


# -------------------------------------------------------------------
# REGISTRO MAESTRO (SOLO SUPERADMIN PLATAFORMA)
# -------------------------------------------------------------------
@router.post("/crear-empresa-master", status_code=status.HTTP_201_CREATED)
def crear_empresa_por_superadmin(
    datos: RegistroEmpresaCreate,
    x_master_key: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint exclusivo para el Superadmin de la plataforma.
    Permite dar de alta una nueva empresa y a su Administrador raíz
    mediante una clave maestra de infraestructura enviada por header HTTP.
    """
    if x_master_key != MASTER_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acceso denegado: Clave maestra de plataforma inválida."
        )

    if crud_usuario.get_usuario_by_email(db, email=datos.email):
        raise HTTPException(status_code=400, detail="El email del administrador ya está registrado.")

    empresa_existente = db.query(Empresa).filter(Empresa.nombre == datos.nombre_empresa).first()
    if empresa_existente:
        raise HTTPException(status_code=400, detail="El nombre de la empresa ya está en uso.")

    nueva_empresa = Empresa(nombre=datos.nombre_empresa)
    db.add(nueva_empresa)
    # flush() para obtener el ID generado sin cerrar la transacción,
    # ya que el usuario necesita empresa_id antes del commit conjunto
    db.flush()

    nuevo_admin = Usuario(
        email=datos.email,
        password_hash=get_password_hash(datos.password),
        rol=RolUsuario.ADMIN,
        empresa_id=nueva_empresa.id
    )
    db.add(nuevo_admin)
    db.commit()

    return {
        "mensaje": f"Empresa '{nueva_empresa.nombre}' creada con éxito.",
        "admin_email": nuevo_admin.email,
        "empresa_id": nueva_empresa.id
    }


# -------------------------------------------------------------------
# CREACIÓN DE EMPLEADOS (SOLO ADMINS)
# -------------------------------------------------------------------
@router.post("/empleados", status_code=status.HTTP_201_CREATED)
def crear_empleado(
    usuario: UsuarioCreate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Permite a un Administrador crear cuentas para miembros de su equipo.
    El nuevo usuario hereda automáticamente la empresa_id del administrador
    que lo crea, garantizando el aislamiento multi-tenant.
    """
    if crud_usuario.get_usuario_by_email(db, email=usuario.email):
        raise HTTPException(status_code=400, detail="Este email ya está registrado.")
        
    nuevo_usuario = Usuario(
        email=usuario.email,
        password_hash=get_password_hash(usuario.password),
        rol=usuario.rol,
        empresa_id=current_user.empresa_id
    )
    
    db.add(nuevo_usuario)
    db.commit()
    
    return {"mensaje": f"Usuario {usuario.email} añadido a tu equipo."}


# -------------------------------------------------------------------
# LOGIN Y PERFIL
# -------------------------------------------------------------------
@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Autentica credenciales y devuelve un JWT con expiración configurable."""
    usuario = crud_usuario.authenticate_usuario(
        db, email=form_data.username, password=form_data.password
    )
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": usuario.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UsuarioResponse)
def read_users_me(current_user: Usuario = Depends(get_current_user)):
    """Devuelve los datos del usuario actualmente autenticado."""
    return current_user


@router.get("/empleados", response_model=List[UsuarioResponse])
def listar_empleados(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """Devuelve todos los usuarios que pertenecen a la misma empresa que el administrador."""
    usuarios = db.query(Usuario).filter(Usuario.empresa_id == current_user.empresa_id).all()
    return usuarios


@router.put("/ajustes")
def actualizar_ajustes(
    ajustes: AjustesUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Actualiza las preferencias y webhooks de notificación del usuario autenticado."""
    current_user.discord_webhook = ajustes.discord_webhook
    current_user.slack_webhook = ajustes.slack_webhook
    if ajustes.recibir_alertas_email is not None:
        current_user.recibir_alertas_email = ajustes.recibir_alertas_email
        
    db.commit()
    db.refresh(current_user)
    
    return {"mensaje": "Ajustes actualizados correctamente"}


@router.get("/empresa/smtp", response_model=EmpresaSMTPResponse)
def obtener_smtp_empresa(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """Recupera los ajustes SMTP de la empresa del administrador autenticado."""
    empresa = current_user.empresa
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
        
    return EmpresaSMTPResponse(
        smtp_host=empresa.smtp_host,
        smtp_port=empresa.smtp_port,
        smtp_user=empresa.smtp_user,
        smtp_from=empresa.smtp_from,
        has_password=bool(empresa.smtp_password)
    )


@router.put("/empresa/smtp")
def actualizar_smtp_empresa(
    smtp_data: EmpresaSMTPUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """Actualiza los ajustes SMTP de la empresa del administrador autenticado."""
    empresa = current_user.empresa
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
        
    empresa.smtp_host = smtp_data.smtp_host
    empresa.smtp_port = smtp_data.smtp_port
    empresa.smtp_user = smtp_data.smtp_user
    empresa.smtp_from = smtp_data.smtp_from
    
    # Solo sobrescribimos la contraseña si el frontend envía una nueva;
    # un campo vacío significa "mantener la existente"
    if smtp_data.smtp_password and smtp_data.smtp_password.strip():
        empresa.smtp_password = smtp_data.smtp_password.strip()
        
    db.commit()
    return {"mensaje": "Configuración SMTP de la empresa actualizada correctamente"}


# -------------------------------------------------------------------
# BORRAR EMPRESA (SOLO SUPERADMIN PLATAFORMA)
# -------------------------------------------------------------------
@router.delete("/empresa-master/{empresa_id}", status_code=status.HTTP_200_OK)
def eliminar_empresa_por_superadmin(
    empresa_id: str,  # str porque el modelo usa UUID como tipo de clave primaria
    x_master_key: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint exclusivo para el Superadmin.
    Elimina una empresa y, por cascada ORM, todos sus usuarios, servidores y métricas.
    """
    if x_master_key != MASTER_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Clave maestra de plataforma inválida.")
    
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada.")
        
    db.delete(empresa)
    db.commit()
    return {"mensaje": f"Empresa '{empresa.nombre}' y toda su infraestructura asociada han sido eliminadas."}


# -------------------------------------------------------------------
# ELIMINAR EMPLEADO (SOLO ADMIN DE LA EMPRESA)
# -------------------------------------------------------------------
@router.delete("/empleados/{usuario_id}", status_code=status.HTTP_200_OK)
def eliminar_empleado(
    usuario_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """Permite a un Administrador eliminar a un miembro de su equipo."""
    
    if str(current_user.id) == str(usuario_id):
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta de administrador.")
    
    # Filtro doble: el usuario debe existir Y pertenecer a la misma empresa que el admin
    empleado = db.query(Usuario).filter(Usuario.id == usuario_id, Usuario.empresa_id == current_user.empresa_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o no pertenece a tu equipo.")
        
    db.delete(empleado)
    db.commit()
    return {"mensaje": "Empleado eliminado correctamente del sistema."}