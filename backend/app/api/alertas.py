from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Alerta, Servidor, Usuario
from app.api.deps import get_current_user

router = APIRouter(tags=["Alertas"])

@router.get("/pendientes")
def obtener_alertas_pendientes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Devuelve las alertas no leídas, filtradas por los permisos del usuario:
    admins ven las de todos sus servidores; técnicos solo las de sus servidores asignados.
    """
    if current_user.rol in ["admin", "superadmin"]:
        servidores_bd = db.query(Servidor.id).filter(Servidor.empresa_id == current_user.empresa_id).all()
        servidores_permitidos = [s.id for s in servidores_bd]
    else:
        servidores_permitidos = [s.id for s in current_user.servidores_supervisados]

    if not servidores_permitidos:
        return []

    alertas = (
        db.query(Alerta)
        .filter(
            Alerta.leida == False,
            Alerta.servidor_id.in_(servidores_permitidos)
        )
        .order_by(Alerta.tiempo.desc())
        .all()
    )
    return alertas


@router.patch("/{alerta_id}/marcar-leida")
def marcar_alerta_leida(
    alerta_id: int, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Marca una alerta como leída tras verificar que el usuario tiene
    permisos sobre el servidor que la generó (mismo tenant + acceso asignado).
    """
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")

    if current_user.rol in ["admin", "superadmin"]:
        servidor = db.query(Servidor).filter(Servidor.id == alerta.servidor_id).first()
        if not servidor or servidor.empresa_id != current_user.empresa_id:
            raise HTTPException(status_code=403, detail="No tienes permisos sobre esta alerta")
    else:
        servidores_permitidos = [s.id for s in current_user.servidores_supervisados]
        if alerta.servidor_id not in servidores_permitidos:
            raise HTTPException(status_code=403, detail="No tienes permisos sobre esta alerta")
            
    alerta.leida = True
    db.commit()
    
    return {"mensaje": "Alerta marcada como leída correctamente", "id": alerta_id}