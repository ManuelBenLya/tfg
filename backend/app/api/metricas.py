from fastapi import APIRouter, Depends, HTTPException, Header, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import hashlib

from app.db.database import get_db, SessionLocal
from app.schemas.metrica import MetricaCreate, MetricaResponse
from app.crud import metrica as crud_metrica
from app.models.models import Servidor, MetricaHardware, Usuario, Alerta
from app.api.deps import get_current_user
from app.models.enums import RolUsuario

router = APIRouter(tags=["Métricas"])

def verificar_token_servidor(
    x_server_token: str = Header(..., description="Token de autenticación del servidor"),
    db: Session = Depends(get_db)
):
    """
    Dependencia que verifica que la máquina que envía las métricas tiene un token válido.
    """
    token_hash = hashlib.sha256(x_server_token.encode()).hexdigest()
    servidor = db.query(Servidor).filter(Servidor.token_auth == token_hash).first()
    
    if not servidor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de servidor inválido o máquina no registrada"
        )
    
    return servidor

    
def evaluar_umbrales_y_alertar_bg(metrica_dict: dict, servidor_id: str):
    db = SessionLocal()
    try:
        servidor = db.query(Servidor).filter(Servidor.id == servidor_id).first()
        if not servidor:
            return
            
        mensaje_alerta = None
        umbral_cpu = servidor.umbral_cpu or 90.0
        umbral_ram = servidor.umbral_ram or 16000.0
        umbral_disco = servidor.umbral_disco or 90.0
        umbral_red = servidor.umbral_red or 500.0
        
        cpu_usage_pct = metrica_dict.get("cpu_usage_pct")
        ram_usage_mb = metrica_dict.get("ram_usage_mb")
        disk_usage_pct = metrica_dict.get("disk_usage_pct")
        network_latency_ms = metrica_dict.get("network_latency_ms")
        
        if cpu_usage_pct is not None and cpu_usage_pct >= umbral_cpu:
            mensaje_alerta = f"Uso de CPU crítico: {cpu_usage_pct}% (Supera el umbral de {umbral_cpu}%)"
        elif ram_usage_mb is not None and ram_usage_mb >= umbral_ram:
            mensaje_alerta = f"Consumo de RAM elevado: {ram_usage_mb}MB (Supera el umbral de {umbral_ram}MB)"
        elif disk_usage_pct is not None and disk_usage_pct >= umbral_disco:
            mensaje_alerta = f"Espacio en disco casi lleno: {disk_usage_pct}% (Supera el umbral de {umbral_disco}%)"
        elif network_latency_ms is not None and network_latency_ms >= umbral_red:
            mensaje_alerta = f"Latencia de red inusual: {network_latency_ms}ms (Supera el umbral de {umbral_red}ms)"
            
        if mensaje_alerta:
            # Debouncing: Buscamos si ya hubo una alerta igual para este servidor en los últimos 15 min
            ultima_alerta = db.query(Alerta).filter(
                Alerta.servidor_id == servidor.id,
                Alerta.mensaje.like(f"{mensaje_alerta[:15]}%") # Misma categoría
            ).order_by(Alerta.tiempo.desc()).first()
            
            hace_15_min = True
            if ultima_alerta:
                tiempo_alerta = ultima_alerta.tiempo
                if tiempo_alerta.tzinfo is None:
                    # Si es naive (ej. SQLite), asumimos UTC
                    tiempo_alerta = tiempo_alerta.replace(tzinfo=timezone.utc)
                else:
                    # Si es aware (ej. PostgreSQL), lo convertimos correctamente a UTC
                    tiempo_alerta = tiempo_alerta.astimezone(timezone.utc)
                hace_15_min = (datetime.now(timezone.utc) - tiempo_alerta) > timedelta(minutes=15)
            
            if not ultima_alerta or hace_15_min:
                nueva_alerta = Alerta(
                    servidor_id=servidor.id,
                    mensaje=mensaje_alerta,
                    leida=False
                )
                db.add(nueva_alerta)
                db.commit()

                # 🌟 ENVIAR NOTIFICACIONES (CORREO, SLACK, DISCORD)
                try:
                    from app.services.notificador import enviar_notificaciones_alerta
                    enviar_notificaciones_alerta(db, servidor, mensaje_alerta)
                except Exception as e:
                    import logging
                    logging.getLogger("uvicorn.error").error(f"Error al enviar notificaciones: {e}")
    finally:
        db.close()

@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_metrica(
    metrica: MetricaCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    servidor: Servidor = Depends(verificar_token_servidor), 
    db: Session = Depends(get_db)
):
    ip_real = request.client.host

    # Actualizamos la IP si ha cambiado
    if servidor.ip_direccion != ip_real:
        servidor.ip_direccion = ip_real 
        db.commit()

    # 1. Guardamos la métrica en la base de datos
    crud_metrica.create_metrica(db=db, metrica=metrica, servidor_id=servidor.id)
    
    # 2. EVALUACIÓN DINÁMICA POR UMBRALES EN SEGUNDO PLANO
    background_tasks.add_task(evaluar_umbrales_y_alertar_bg, metrica.model_dump() if hasattr(metrica, 'model_dump') else metrica.dict(), str(servidor.id))
    
    return {"status": "ok"}


@router.get("/{servidor_id}", response_model=List[MetricaResponse])
def obtener_historial_metricas(
    servidor_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Recupera el historial reciente de una máquina concreta.
    """
    # Usar subquery para obtener las ultimas N metricas y luego ordenarlas ascendente
    subquery = (
        db.query(MetricaHardware)
        .filter(MetricaHardware.servidor_id == servidor_id)
        .order_by(MetricaHardware.tiempo.desc())
        .limit(limit)
        .subquery()
    )
    
    from sqlalchemy.orm import aliased
    MetricaAlias = aliased(MetricaHardware, subquery)
    
    metricas = db.query(MetricaAlias).order_by(MetricaAlias.tiempo.asc()).all()
    return metricas


@router.get("/", response_model=List[MetricaResponse])
def obtener_metricas_globales(
    rango: Optional[str] = '1h', 
    servidor_id: Optional[str] = None, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Devuelve las métricas filtradas por tiempo Y por los permisos del usuario.
    """
    ahora = datetime.now(timezone.utc)
    
    if rango == '15m': fecha_limite = ahora - timedelta(minutes=15)
    elif rango == '1h': fecha_limite = ahora - timedelta(hours=1)
    elif rango == '24h': fecha_limite = ahora - timedelta(hours=24)
    elif rango == '7d': fecha_limite = ahora - timedelta(days=7)
    else: fecha_limite = ahora - timedelta(hours=1)

    # 🌟 1. LÓGICA DE SEGURIDAD (RBAC)
    if current_user.rol == RolUsuario.ADMIN or current_user.rol == "superadmin":
        # Los admins pueden ver todos los servidores de SU empresa
        servidores_bd = db.query(Servidor.id).filter(Servidor.empresa_id == current_user.empresa_id).all()
        servidores_permitidos = {s.id for s in servidores_bd}
    else:
        # Los técnicos SOLO ven los que se les han asignado en la tabla intermedia
        servidores_permitidos = {s.id for s in current_user.servidores_supervisados}

    # Si es un técnico sin servidores asignados, no buscamos nada, devolvemos vacío
    if not servidores_permitidos:
        return []

    # 🌟 2. CONSULTA FILTRADA
    # Solo traemos las métricas de los servidores que están en su lista de permitidos
    query = db.query(MetricaHardware).filter(
        MetricaHardware.tiempo >= fecha_limite,
        MetricaHardware.servidor_id.in_(list(servidores_permitidos))
    )

    if servidor_id:
        # Si pide un servidor específico, verificamos que no intente espiar otro
        import uuid
        try:
            sid = uuid.UUID(servidor_id)
            if sid not in servidores_permitidos and str(sid) not in servidores_permitidos:
                raise HTTPException(status_code=403, detail="Acceso denegado a este servidor.")
        except ValueError:
            raise HTTPException(status_code=400, detail="ID de servidor inválido.")
        query = query.filter(MetricaHardware.servidor_id == sid)

    metricas = query.order_by(MetricaHardware.tiempo.asc()).all()
    return metricas