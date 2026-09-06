from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import InvalidTokenError

# Ajusta las importaciones según la estructura exacta de tu proyecto
from app.core.security import SECRET_KEY, ALGORITHM
from app.schemas.usuario import TokenData
from app.models.models import Usuario
from app.models.enums import RolUsuario
from app.db.database import get_db # Asumiendo que aquí tienes tu función para obtener la BD

# Esto le dice a FastAPI dónde está el endpoint de login que acabamos de hacer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/usuarios/login")

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    """
    Dependencia que intercepta el Token JWT, lo decodifica y devuelve el usuario autenticado.
    Si el token es inválido o expiró, bloquea el acceso con un error 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificamos el token usando la misma clave y algoritmo
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extraemos el "sub" (subject) que guardamos al hacer login, que era el email
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
        # Lo validamos con nuestro esquema de Pydantic
        token_data = TokenData(email=email)
        
    except InvalidTokenError:
        # Si el token fue modificado, es falso o ha caducado, salta aquí
        raise credentials_exception
        
    # Buscamos al usuario en la base de datos por su email
    usuario = db.query(Usuario).filter(Usuario.email == token_data.email).first()
    
    if usuario is None:
        raise credentials_exception
        
    return usuario


def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """
    Dependencia reutilizable que garantiza que el usuario autenticado es administrador.
    Úsala con Depends(require_admin) en endpoints que requieran permisos de admin.
    """
    if current_user.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador."
        )
    return current_user