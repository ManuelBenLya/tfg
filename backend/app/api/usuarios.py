from fastapi import APIRouter, Depends, HTTPException, status, Header # 🌟 Añadido Header aquí
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import os

# Importaciones de tu base de datos y seguridad
from app.db.database import SessionLocal
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, Token, RegistroEmpresaCreate, AjustesUpdate
from app.crud import usuario as crud_usuario
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import get_password_hash 
from app.api.deps import get_current_user
from app.models.models import Usuario, Empresa 
from typing import List

router = APIRouter()
MASTER_SECRET_KEY = os.getenv("MASTER_SECRET_KEY", "clave-maestra-tfg-2026-secure")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------------------------------------------
# 1. REGISTRO MAESTRO (SOLO SUPERADMIN PLATAFORMA)
# -------------------------------------------------------------------
@router.post("/crear-empresa-master", status_code=status.HTTP_201_CREATED)
def crear_empresa_por_superadmin(
    datos: RegistroEmpresaCreate,
    x_master_key: str = Header(...), # 🌟 Exigimos la cabecera secreta
    db: Session = Depends(get_db)
):
    """
    Endpoint exclusivo para el Superadmin de la plataforma. 
    Permite dar de alta una nueva empresa y a su Administrador raíz 
    mediante una clave maestra de infraestructura.
    """
    # 1. Validar la llave maestra
    if x_master_key != MASTER_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acceso denegado: Clave maestra de plataforma inválida."
        )

    # 2. Comprobar si el email ya existe
    if crud_usuario.get_usuario_by_email(db, email=datos.email):
        raise HTTPException(status_code=400, detail="El email del administrador ya está registrado.")

    # 3. Comprobar si la empresa ya existe
    empresa_existente = db.query(Empresa).filter(Empresa.nombre == datos.nombre_empresa).first()
    if empresa_existente:
        raise HTTPException(status_code=400, detail="El nombre de la empresa ya está en uso.")

    # 4. Crear la Empresa
    nueva_empresa = Empresa(nombre=datos.nombre_empresa)
    db.add(nueva_empresa)
    db.flush()

    # 5. Crear el Usuario Administrador vinculado
    nuevo_admin = Usuario(
        email=datos.email,
        password_hash=get_password_hash(datos.password),
        rol="admin",
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
# 2. CREACIÓN DE EMPLEADOS (SOLO ADMINS)
# -------------------------------------------------------------------
@router.post("/empleados", status_code=status.HTTP_201_CREATED)
def crear_empleado(
    usuario: UsuarioCreate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user) # 🔒 Protegido
):
    """
    Permite a un Administrador crear cuentas para su equipo.
    Los nuevos usuarios se asignan automáticamente a la empresa del Administrador.
    """
    # 1. Verificar que quien hace la petición es ADMIN
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo los administradores pueden añadir personal.")
        
    # 2. Comprobar si el email ya existe
    if crud_usuario.get_usuario_by_email(db, email=usuario.email):
        raise HTTPException(status_code=400, detail="Este email ya está registrado.")
        
    # 3. Crear el nuevo usuario
    nuevo_usuario = Usuario(
        email=usuario.email,
        password_hash=get_password_hash(usuario.password),
        rol=usuario.rol, # "admin" o "usuario" (según lo que envíe el formulario)
        empresa_id=current_user.empresa_id # 🌟 Se le inyecta la empresa de su jefe
    )
    
    db.add(nuevo_usuario)
    db.commit()
    
    return {"mensaje": f"Usuario {usuario.email} añadido a tu equipo."}


# -------------------------------------------------------------------
# 3. LOGIN Y PERFIL (TUS ENDPOINTS ORIGINALES INTACTOS)
# -------------------------------------------------------------------
@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint para iniciar sesión. Recibe credenciales y devuelve un JWT.
    """
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
    """
    Devuelve los datos del usuario actualmente autenticado.
    """
    return current_user



@router.get("/empleados", response_model=List[UsuarioResponse])
def listar_empleados(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Devuelve todos los usuarios que pertenecen a la misma empresa que el Administrador.
    """
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos.")
        
    usuarios = db.query(Usuario).filter(Usuario.empresa_id == current_user.empresa_id).all()
    return usuarios


@router.put("/ajustes")
def actualizar_ajustes(
    ajustes: AjustesUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza las preferencias y webhooks de alerta del usuario autenticado.
    """
    # Si tus columnas en la base de datos se llaman así, las actualizamos:
    if hasattr(current_user, "discord_webhook"):
        current_user.discord_webhook = ajustes.discord_webhook
    if hasattr(current_user, "slack_webhook"):
        current_user.slack_webhook = ajustes.slack_webhook
        
    db.commit()
    db.refresh(current_user)
    
    return {"mensaje": "Ajustes actualizados correctamente"}