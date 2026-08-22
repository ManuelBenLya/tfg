from sqlalchemy.orm import Session
import secrets

from app.models.models import Servidor
from app.schemas.servidor import ServidorCreate

def create_servidor(db: Session, servidor: ServidorCreate, empresa_id: str):
    """
    Crea un servidor nuevo generando un token de autenticación único y seguro,
    y lo vincula a la empresa del administrador.
    """
    # Generamos un token aleatorio de 32 bytes en formato URL safe
    token_seguro = secrets.token_urlsafe(32)
    
    db_servidor = Servidor(
        nombre=servidor.nombre,
        ip_direccion=servidor.ip_direccion,
        estado=servidor.estado,
        token_auth=token_seguro,
        empresa_id=empresa_id  # Ahora Python sí sabe de dónde viene esta variable
    )
    
    db.add(db_servidor)
    db.commit()
    db.refresh(db_servidor)
    
    return db_servidor

def get_servidores(db: Session, skip: int = 0, limit: int = 100):
    """
    Devuelve la lista de servidores registrados.
    """
    return db.query(Servidor).offset(skip).limit(limit).all()