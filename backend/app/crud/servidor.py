from sqlalchemy.orm import Session
import secrets
import hashlib

from app.models.models import Servidor, Usuario
from app.schemas.servidor import ServidorCreate


def create_servidor(db: Session, servidor: ServidorCreate, empresa_id: str, admin: Usuario):
    """
    Crea un servidor nuevo generando un token de autenticación único y seguro,
    lo vincula a la empresa del administrador y le asigna acceso al admin.
    Todo en una sola transacción atómica.
    """
    # Generamos un token aleatorio de 32 bytes en formato URL safe
    token_seguro = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token_seguro.encode()).hexdigest()
    
    db_servidor = Servidor(
        nombre=servidor.nombre,
        ip_direccion=servidor.ip_direccion,
        estado=servidor.estado,
        token_auth=token_hash,
        empresa_id=empresa_id
    )
    
    # Vinculación automática: el admin que crea el servidor obtiene acceso
    db_servidor.usuarios_con_acceso.append(admin)
    
    db.add(db_servidor)
    db.commit()
    db.refresh(db_servidor)
    
    # Excluimos el objeto de la sesión para evitar que SQLAlchemy
    # guarde el token en texto plano en la base de datos por accidente.
    db.expunge(db_servidor)
    
    # Reemplazamos temporalmente el token hasheado por el token plano
    # para que la respuesta de FastAPI (ServidorResponse) pueda mostrarlo al usuario.
    db_servidor.token_auth = token_seguro
    
    return db_servidor

def obtener_promedio_metricas_24h(db: Session, servidor_id):
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