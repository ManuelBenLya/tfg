from fastapi import APIRouter, Depends, HTTPException, Header, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.schemas.metrica import MetricaCreate, MetricaResponse
from app.crud import metrica as crud_metrica
from app.models.models import Servidor, MetricaHardware, Usuario, Alerta
from app.api.deps import get_current_user 

router = APIRouter(tags=["Métricas"])

def verificar_token_servidor(
    x_server_token: str = Header(..., description="Token de autenticación del servidor"),
    db: Session = Depends(get_db)
):
    """
    Dependencia que verifica que la máquina que envía las métricas tiene un token válido.
    """
    servidor = db.query(Servidor).filter(Servidor.token_auth == x_server_token).first()
    
    if not servidor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de servidor inválido o máquina no registrada"
        )
    
    return servidor

    
@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_metrica(
    metrica: MetricaCreate,
    request: Request,
    servidor: Servidor = Depends(verificar_token_servidor), 
    db: Session = Depends(get_db)
):
    # Extraemos la IP real desde donde el agente está mandando los datos
    ip_real = request.client.host

    # Actualizamos el estado a Online Y la IP si ha cambiado
    ha_cambiado = False
    if servidor.estado != "Online":
        servidor.estado = "Online"
        ha_cambiado = True
        
    if servidor.ip_direccion != ip_real:
        servidor.ip_direccion = ip_real 
        ha_cambiado = True
        
    if ha_cambiado:
        db.commit()

    # 1. Guardamos la métrica en la base de datos
    crud_metrica.create_metrica(db=db, metrica=metrica, servidor_id=servidor.id)
    
    # 2. EVALUACIÓN DINÁMICA POR UMBRALES
    mensaje_alerta = None
    umbral_cpu = servidor.umbral_cpu or 90.0
    umbral_ram = servidor.umbral_ram or 16000.0
    umbral_disco = servidor.umbral_disco or 90.0
    umbral_red = servidor.umbral_red or 500.0
    
    if metrica.cpu_usage_pct is not None and metrica.cpu_usage_pct >= umbral_cpu:
        mensaje_alerta = f"Uso de CPU crítico: {metrica.cpu_usage_pct}% (Supera el umbral de {umbral_cpu}%)"
        
    elif metrica.ram_usage_mb is not None and metrica.ram_usage_mb >= umbral_ram:
        mensaje_alerta = f"Consumo de RAM elevado: {metrica.ram_usage_mb}MB (Supera el umbral de {umbral_ram}MB)"
        
    elif metrica.disk_usage_pct is not None and metrica.disk_usage_pct >= umbral_disco:
        mensaje_alerta = f"Espacio en disco casi lleno: {metrica.disk_usage_pct}% (Supera el umbral de {umbral_disco}%)"
        
    elif metrica.network_latency_ms is not None and metrica.network_latency_ms >= umbral_red:
        mensaje_alerta = f"Latencia de red inusual: {metrica.network_latency_ms}ms (Supera el umbral de {umbral_red}ms)"
        
    # 3. Guardar la alerta
    if mensaje_alerta:
        nueva_alerta = Alerta(
            servidor_id=servidor.id,
            mensaje=mensaje_alerta,
            leida=False
        )
        db.add(nueva_alerta)
        db.commit()
    
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
    metricas = (
        db.query(MetricaHardware)
        .filter(MetricaHardware.servidor_id == servidor_id)
        .order_by(MetricaHardware.tiempo.desc())
        .limit(limit)
        .all()
    )
    metricas.reverse()
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
    ahora = datetime.utcnow()
    
    if rango == '15m': fecha_limite = ahora - timedelta(minutes=15)
    elif rango == '1h': fecha_limite = ahora - timedelta(hours=1)
    elif rango == '24h': fecha_limite = ahora - timedelta(hours=24)
    elif rango == '7d': fecha_limite = ahora - timedelta(days=7)
    else: fecha_limite = ahora - timedelta(hours=1)

    # 🌟 1. LÓGICA DE SEGURIDAD (RBAC)
    if current_user.rol == "admin" or current_user.rol == "superadmin":
        # Los admins pueden ver todos los servidores de SU empresa
        servidores_bd = db.query(Servidor.id).filter(Servidor.empresa_id == current_user.empresa_id).all()
        servidores_permitidos = [s.id for s in servidores_bd]
    else:
        # Los técnicos SOLO ven los que se les han asignado en la tabla intermedia
        servidores_permitidos = [s.id for s in current_user.servidores_supervisados]

    # Si es un técnico sin servidores asignados, no buscamos nada, devolvemos vacío
    if not servidores_permitidos:
        return []

    # 🌟 2. CONSULTA FILTRADA
    # Solo traemos las métricas de los servidores que están en su lista de permitidos
    query = db.query(MetricaHardware).filter(
        MetricaHardware.tiempo >= fecha_limite,
        MetricaHardware.servidor_id.in_(servidores_permitidos)
    )

    if servidor_id:
        # Si pide un servidor específico, verificamos que no intente espiar otro
        if str(servidor_id) not in [str(id) for id in servidores_permitidos]:
            raise HTTPException(status_code=403, detail="Acceso denegado a este servidor.")
        query = query.filter(MetricaHardware.servidor_id == servidor_id)

    metricas = query.order_by(MetricaHardware.tiempo.asc()).all()
    return metricas