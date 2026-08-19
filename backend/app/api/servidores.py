from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.db.database import get_db
from app.schemas.servidor import ServidorCreate, ServidorResponse, UmbralesUpdate
from app.crud import servidor as crud_servidor
from app.api.deps import get_current_user
from app.models.models import Usuario, Servidor, MetricaHardware

router = APIRouter(tags=["Servidores"])

@router.post("/", response_model=ServidorResponse, status_code=status.HTTP_201_CREATED)
def crear_servidor(
    servidor: ServidorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user) # 🔒 ¡Ruta protegida!
):
    """
    Registra un nuevo servidor en la infraestructura. Devuelve el token generado.
    """
    return crud_servidor.create_servidor(db=db, servidor=servidor)

@router.get("/", response_model=List[ServidorResponse])
def listar_servidores(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user) # 🔒 ¡Ruta protegida!
):
    """
    Lista todos los servidores registrados en el sistema y actualiza 
    dinámicamente su estado (Online/Offline) basándose en su última métrica.
    """
    # 1. Obtenemos los servidores con tu función CRUD
    servidores = crud_servidor.get_servidores(db, skip=skip, limit=limit)
    
    # 2. Límite de 15 segundos para considerar que se ha caído
    limite_tiempo = datetime.utcnow() - timedelta(seconds=15)
    
    # 3. Comprobación perezosa (Lazy Validation)
    for servidor in servidores:
        ultima_metrica = (
            db.query(MetricaHardware)
            .filter(MetricaHardware.servidor_id == servidor.id)
            .order_by(MetricaHardware.tiempo.desc())
            .first()
        )
        
        if not ultima_metrica:
            servidor.estado = "Offline"
        elif ultima_metrica.tiempo < limite_tiempo:
            servidor.estado = "Offline"
        else:
            servidor.estado = "Online"
            
    # 4. Guardamos los cambios en PostgreSQL
    db.commit()
    
    # 5. Devolvemos la lista actualizada al frontend
    return servidores

@router.patch("/{servidor_id}/umbrales")
def actualizar_umbrales(
    servidor_id: str, 
    umbrales: UmbralesUpdate, 
    db: Session = Depends(get_db)
):
    """
    Actualiza los umbrales de alerta estáticos de un servidor específico.
    """
    servidor = db.query(Servidor).filter(Servidor.id == servidor_id).first()
    
    if not servidor:
        raise HTTPException(status_code=404, detail="Servidor no encontrado")
        
    # Actualizamos los valores
    servidor.umbral_cpu = umbrales.umbral_cpu
    servidor.umbral_ram = umbrales.umbral_ram
    servidor.umbral_disco = umbrales.umbral_disco
    servidor.umbral_red = umbrales.umbral_red
    
    db.commit()
    
    return {"mensaje": "Umbrales actualizados correctamente"}