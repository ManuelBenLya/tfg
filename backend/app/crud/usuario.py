from sqlalchemy.orm import Session
from app.models.models import Usuario
from app.schemas.usuario import UsuarioCreate
from app.core.security import get_password_hash
from app.core.security import verify_password


def get_usuario_by_email(db: Session, email: str):
    """Busca un usuario por su correo electrónico."""
    return db.query(Usuario).filter(Usuario.email == email).first()

def create_usuario(db: Session, usuario: UsuarioCreate):
    """Crea un nuevo usuario encriptando su contraseña."""
    
    # 1. Usamos nuestra herramienta del core para generar el hash seguro
    hashed_password = get_password_hash(usuario.password)
    
    # 2. Construimos el modelo de SQLAlchemy
    db_usuario = Usuario(
        email=usuario.email,
        password_hash=hashed_password,
        rol=usuario.rol
    )
    
    # 3. Insertamos y guardamos los cambios en PostgreSQL
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario


def authenticate_usuario(db: Session, email: str, password: str):
    """
    Busca al usuario por email y verifica que la contraseña sea correcta.
    Devuelve el usuario si todo está bien, o False si falla algo.
    """
    usuario = get_usuario_by_email(db, email=email)
    
    # Si el usuario no existe en la base de datos
    if not usuario:
        return False
        
    # Si la contraseña no coincide con el hash guardado
    if not verify_password(password, usuario.password_hash):
        return False
        
    return usuario

