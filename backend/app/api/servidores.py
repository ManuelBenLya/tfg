import re
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func
from typing import List
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.db.database import get_db
from app.schemas.servidor import (
    ServidorCreate, ServidorResponse, UmbralesUpdate, 
    ServidorUpdate, AsignarUsuariosRequest, MensajeResponse
)
from app.crud import servidor as crud_servidor
from app.api.deps import get_current_user, require_admin
from app.models.models import Usuario, Servidor, MetricaHardware
from fastapi.responses import StreamingResponse
from app.services.pdf_generator import crear_reporte_pdf


router = APIRouter(tags=["Servidores"])


# -------------------------------------------------------------------
# DEPENDENCIAS REUSABLES
# -------------------------------------------------------------------
def get_servidor_admin(
    servidor_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
) -> Servidor:
    """Obtiene un servidor verificando que pertenece a la empresa del administrador."""
    servidor = db.query(Servidor).filter(
        Servidor.id == servidor_id,
        Servidor.empresa_id == current_user.empresa_id
    ).first()
    if not servidor:
        raise HTTPException(status_code=404, detail="Servidor no encontrado.")
    return servidor

def get_servidor_permitido(
    servidor_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Servidor:
    """Obtiene un servidor verificando que el usuario tiene acceso asignado mediante la tabla intermedia."""
    servidor = db.query(Servidor).filter(
        Servidor.id == servidor_id,
        Servidor.empresa_id == current_user.empresa_id,
        Servidor.usuarios_con_acceso.any(id=current_user.id)
    ).first()
    if not servidor:
        raise HTTPException(status_code=404, detail="Servidor no encontrado o sin acceso.")
    return servidor


@router.post("/", response_model=ServidorResponse, status_code=status.HTTP_201_CREATED)
def crear_servidor(
    servidor: ServidorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """Registra un nuevo servidor y devuelve el token de autenticación en texto plano (solo esta vez)."""
    nuevo_servidor = crud_servidor.create_servidor(
        db=db, 
        servidor=servidor, 
        empresa_id=current_user.empresa_id,
        admin=current_user
    )
    
    # Guardamos el token plano antes de re-consultar, porque el CRUD lo expunge
    # de la sesión y la re-consulta devolvería el hash SHA-256 almacenado en BD
    token_limpio = nuevo_servidor.token_auth
    servidor_fresco = db.query(Servidor).filter(Servidor.id == nuevo_servidor.id).first()
    servidor_fresco.token_auth = token_limpio
    
    return servidor_fresco


@router.get("/", response_model=List[ServidorResponse])
def listar_servidores(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Devuelve los servidores a los que el usuario tiene acceso asignado
    y calcula su estado Online/Offline en función de la última métrica recibida.
    """
    servidores = current_user.servidores_supervisados
    
    if not servidores:
        return servidores
    
    ids = [s.id for s in servidores]
    
    # Subquery agrupada para obtener la última métrica de cada servidor en una sola consulta,
    # evitando el problema N+1 (una query por servidor)
    ultima_metrica_sub = (
        db.query(
            MetricaHardware.servidor_id,
            sa_func.max(MetricaHardware.tiempo).label("ultimo_tiempo")
        )
        .filter(MetricaHardware.servidor_id.in_(ids))
        .group_by(MetricaHardware.servidor_id)
        .all()
    )
    
    mapa_tiempos = {r.servidor_id: r.ultimo_tiempo for r in ultima_metrica_sub}
    limite_tiempo = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=15)
    
    for servidor in servidores:
        ultimo = mapa_tiempos.get(servidor.id)
        servidor.estado = "Online" if ultimo and ultimo >= limite_tiempo else "Offline"
            
    return servidores


@router.patch("/{servidor_id}/umbrales", response_model=MensajeResponse)
def actualizar_umbrales(
    umbrales: UmbralesUpdate, 
    db: Session = Depends(get_db),
    servidor: Servidor = Depends(get_servidor_admin)
):
    """Actualiza los umbrales de alerta de un servidor. Solo accesible por administradores."""
    servidor.umbral_cpu = umbrales.umbral_cpu
    servidor.umbral_ram = umbrales.umbral_ram
    servidor.umbral_disco = umbrales.umbral_disco
    servidor.umbral_red = umbrales.umbral_red
    
    db.commit()
    return {"mensaje": "Umbrales actualizados correctamente"}


@router.put("/{servidor_id}/asignar-usuarios", response_model=MensajeResponse)
def asignar_usuarios_a_servidor(
    request: AsignarUsuariosRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
    servidor: Servidor = Depends(get_servidor_admin)
):
    """
    Define qué usuarios pueden supervisar un servidor concreto.
    Sobrescribe la lista completa; SQLAlchemy gestiona las operaciones
    DELETE/INSERT en la tabla intermedia usuario_servidor automáticamente.
    """
    usuarios_a_asignar = db.query(Usuario).filter(
        Usuario.id.in_(request.usuario_ids),
        Usuario.empresa_id == current_user.empresa_id
    ).all()

    servidor.usuarios_con_acceso = usuarios_a_asignar
    db.commit()

    return {"mensaje": "Accesos actualizados correctamente"}


@router.get("/{servidor_id}/reporte-pdf")
def descargar_reporte_pdf(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    servidor: Servidor = Depends(get_servidor_permitido)
):
    """
    Genera un reporte PDF con las métricas promedio de las últimas 24 horas.
    Solo accesible para usuarios con acceso asignado al servidor.
    """
    resultado = crud_servidor.obtener_promedio_metricas_24h(db, servidor.id)

    if not resultado:
        metricas_resumen = {"cpu_avg": 0.0, "ram_avg": 0.0, "disco_avg": 0.0}
    else:
        metricas_resumen = {
            "cpu_avg": round(resultado.cpu_avg, 2) if resultado.cpu_avg is not None else 0.0,
            "ram_avg": round(resultado.ram_avg, 2) if resultado.ram_avg is not None else 0.0,
            "disco_avg": round(resultado.disco_avg, 2) if resultado.disco_avg is not None else 0.0,
        }

    pdf_buffer = crear_reporte_pdf(servidor, metricas_resumen, current_user.email)

    # Sanitización para evitar inyección de caracteres especiales en el header Content-Disposition
    nombre_limpio = re.sub(r'[^\w\s-]', '', servidor.nombre).strip()
    headers = {
        'Content-Disposition': f'attachment; filename="Reporte_{nombre_limpio}.pdf"'
    }
    
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)


# -------------------------------------------------------------------
# EDITAR NOMBRE DEL SERVIDOR
# -------------------------------------------------------------------
@router.put("/{servidor_id}", response_model=MensajeResponse, status_code=status.HTTP_200_OK)
def actualizar_servidor(
    datos: ServidorUpdate,
    db: Session = Depends(get_db),
    servidor: Servidor = Depends(get_servidor_admin)
):
    """Permite a un administrador actualizar el nombre de un servidor de su empresa."""
    servidor.nombre = datos.nombre
    db.commit()
    return {"mensaje": "Nombre del servidor actualizado correctamente."}


# -------------------------------------------------------------------
# ELIMINAR SERVIDOR (Y SUS MÉTRICAS)
# -------------------------------------------------------------------
@router.delete("/{servidor_id}", response_model=MensajeResponse, status_code=status.HTTP_200_OK)
def eliminar_servidor(
    db: Session = Depends(get_db),
    servidor: Servidor = Depends(get_servidor_admin)
):
    """
    Elimina un servidor y toda su información asociada.
    Las métricas y alertas se eliminan en cascada gracias a la configuración del modelo ORM.
    """
    db.delete(servidor)
    db.commit()
    return {"mensaje": "Servidor y todas sus métricas eliminados correctamente."}