from sqlalchemy.orm import Session
from app.models.models import Usuario
from app.schemas.usuario import UsuarioCreate
from app.core.security import get_password_hash
from app.core.security import verify_password


def get_usuario_by_email(db: Session, email: str):
    """Busca un usuario por su correo electrónico."""
    return db.query(Usuario).filter(Usuario.email == email).first()

def create_usuario(db: Session, usuario: UsuarioCreate):
    """Crea un nuevo usuario encriptando su contraseña con bcrypt."""
    hashed_password = get_password_hash(usuario.password)
    
    db_usuario = Usuario(
        email=usuario.email,
        password_hash=hashed_password,
        rol=usuario.rol
    )
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario


def authenticate_usuario(db: Session, email: str, password: str):
    """
    Autentica un usuario por email y contraseña.
    Devuelve el objeto Usuario si las credenciales son válidas, o False en caso contrario.
    """
    usuario = get_usuario_by_email(db, email=email)
    
    if not usuario:
        return False
        
    if not verify_password(password, usuario.password_hash):
        return False
        
    return usuario
