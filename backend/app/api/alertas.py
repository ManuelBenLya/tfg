from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Alerta

router = APIRouter(tags=["Alertas"])

@router.get("/pendientes")
def obtener_alertas_pendientes(db: Session = Depends(get_db)):
    """
    Devuelve las alertas generadas por la superación de umbrales 
    que aún no han sido marcadas como leídas.
    """
    alertas = db.query(Alerta).filter(Alerta.leida == False).order_by(Alerta.tiempo.desc()).all()
    return alertas

@router.patch("/{alerta_id}/marcar-leida")
def marcar_alerta_leida(alerta_id: int, db: Session = Depends(get_db)):
    """
    Marca una alerta específica como leída usando su ID para que 
    deje de aparecer como pendiente en el Dashboard.
    """
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
        
    alerta.leida = True
    db.commit()
    
    return {"mensaje": "Alerta marcada como leída correctamente", "id": alerta_id}