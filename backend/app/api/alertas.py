from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Alerta, Servidor, Usuario
from app.api.deps import get_current_user

router = APIRouter(tags=["Alertas"])

@router.get("/pendientes")
def obtener_alertas_pendientes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user) # 🔒 Protegido
):
    """
    Devuelve las alertas generadas por la superación de umbrales 
    que aún no han sido marcadas como leídas, filtradas por permisos.
    """
    # 1. Determinar qué servidores puede ver este usuario
    if current_user.rol in ["admin", "superadmin"]:
        servidores_bd = db.query(Servidor.id).filter(Servidor.empresa_id == current_user.empresa_id).all()
        servidores_permitidos = [s.id for s in servidores_bd]
    else:
        servidores_permitidos = [s.id for s in current_user.servidores_supervisados]

    # Si es técnico y no tiene servidores asignados, no hay alertas
    if not servidores_permitidos:
        return []

    # 2. Buscar solo las alertas de SUS servidores permitidos
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
    current_user: Usuario = Depends(get_current_user) # 🔒 Protegido
):
    """
    Marca una alerta específica como leída comprobando que el usuario
    tenga permisos sobre el servidor que la generó.
    """
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")

    # 1. Verificar que el usuario tenga permisos sobre esa alerta
    if current_user.rol in ["admin", "superadmin"]:
        # El administrador debe ser de la misma empresa que el servidor de la alerta
        servidor = db.query(Servidor).filter(Servidor.id == alerta.servidor_id).first()
        if not servidor or servidor.empresa_id != current_user.empresa_id:
            raise HTTPException(status_code=403, detail="No tienes permisos sobre esta alerta")
    else:
        # El técnico debe tener el servidor asignado en su lista
        servidores_permitidos = [s.id for s in current_user.servidores_supervisados]
        if alerta.servidor_id not in servidores_permitidos:
            raise HTTPException(status_code=403, detail="No tienes permisos sobre esta alerta")
            
    # 2. Si pasa las pruebas, la marcamos como leída
    alerta.leida = True
    db.commit()
    
    return {"mensaje": "Alerta marcada como leída correctamente", "id": alerta_id}