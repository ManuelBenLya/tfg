from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Importamos la sesión de tu base de datos, los esquemas y el CRUD
from app.db.database import SessionLocal
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, Token
from app.crud import usuario as crud_usuario

from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

from app.api.deps import get_current_user
from app.models.models import Usuario

router = APIRouter()

# Dependencia: gestiona el ciclo de vida de la conexión a la BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema.
    """
    # 1. Comprobamos si el correo ya existe
    db_user = crud_usuario.get_usuario_by_email(db, email=usuario.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El email ya está registrado en el sistema."
        )
    
    # 2. Si no existe, lo creamos usando tu función segura del CRUD
    return crud_usuario.create_usuario(db=db, usuario=usuario)


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint para iniciar sesión. Recibe credenciales y devuelve un JWT.
    """
    # 1. Verificamos las credenciales en la base de datos
    # Nota: OAuth2PasswordRequestForm siempre usa 'username' por defecto, 
    # por eso mapeamos form_data.username a nuestro campo 'email'.
    usuario = crud_usuario.authenticate_usuario(
        db, email=form_data.username, password=form_data.password
    )
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Calculamos la expiración y generamos el token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Usamos "sub" (subject) que es el estándar en JWT para identificar al usuario
    access_token = create_access_token(
        data={"sub": usuario.email}, expires_delta=access_token_expires
    )
    
    # 3. Devolvemos el token con la estructura exacta de nuestro esquema Pydantic
    return {"access_token": access_token, "token_type": "bearer"}



@router.get("/me", response_model=UsuarioResponse)
def read_users_me(current_user: Usuario = Depends(get_current_user)):
    """
    Devuelve los datos del usuario actualmente autenticado.
    Está protegido: si no envías un JWT válido, no puedes entrar.
    """
    # Gracias a la dependencia get_current_user, FastAPI ya hizo todo el trabajo sucio.
    # Si el código llega hasta aquí, es que el token es válido y ya tenemos el objeto del usuario.
    return current_user