from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import InvalidTokenError

from app.core.security import SECRET_KEY, ALGORITHM
from app.schemas.usuario import TokenData
from app.models.models import Usuario
from app.models.enums import RolUsuario
from app.db.database import get_db

# tokenUrl debe coincidir con la ruta real del endpoint de login para que Swagger UI lo detecte
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/usuarios/login")

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    """
    Dependencia de inyección que intercepta el JWT del header Authorization,
    lo decodifica y devuelve el usuario autenticado.
    Bloquea con HTTP 401 si el token es inválido, expirado o el usuario no existe.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
        
    usuario = db.query(Usuario).filter(Usuario.email == token_data.email).first()
    
    if usuario is None:
        raise credentials_exception
        
    return usuario


def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """
    Dependencia reutilizable que garantiza que el usuario autenticado posee rol de administrador.
    Úsala con Depends(require_admin) en endpoints que requieran permisos elevados.
    """
    if current_user.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador."
        )
    return current_user