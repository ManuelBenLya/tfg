from sqlalchemy.orm import Session
import secrets
import hashlib

from app.models.models import Servidor, Usuario
from app.schemas.servidor import ServidorCreate


def create_servidor(db: Session, servidor: ServidorCreate, empresa_id: str, admin: Usuario):
    """
    Crea un servidor con un token de autenticación único SHA-256.
    Devuelve el objeto con el token en texto plano (solo visible en esta respuesta).
    """
    token_seguro = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token_seguro.encode()).hexdigest()
    
    db_servidor = Servidor(
        nombre=servidor.nombre,
        ip_direccion=servidor.ip_direccion,
        estado=servidor.estado,
        token_auth=token_hash,
        empresa_id=empresa_id
    )
    
    # El admin que registra el servidor obtiene acceso automáticamente
    db_servidor.usuarios_con_acceso.append(admin)
    
    db.add(db_servidor)
    db.commit()
    db.refresh(db_servidor)
    
    # Expunge desvincula el objeto de la sesión para que podamos sustituir
    # el hash por el token plano sin que SQLAlchemy persista ese cambio en BD
    db.expunge(db_servidor)
    db_servidor.token_auth = token_seguro
    
    return db_servidor

def obtener_promedio_metricas_24h(db: Session, servidor_id):
    """Consulta la vista materializada continua de TimescaleDB para obtener promedios de las últimas 24h."""
    from sqlalchemy import text
    
    query = text("""
        SELECT 
            AVG(cpu_avg) as cpu_avg, 
            AVG(ram_avg) as ram_avg, 
            AVG(disco_avg) as disco_avg
        FROM metricas_promedio_1h
        WHERE servidor_id = :servidor_id 
          AND bucket >= NOW() - INTERVAL '24 hours'
    """)
    
    resultado = db.execute(query, {"servidor_id": str(servidor_id)}).fetchone()
    
    return resultado