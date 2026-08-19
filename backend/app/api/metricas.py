from fastapi import APIRouter, Depends, HTTPException, Header, status, Request
from sqlalchemy.orm import Session
from typing import List 

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
    request: Request, # 🌟 NUEVO: FastAPI nos inyecta los datos de la conexión real
    servidor: Servidor = Depends(verificar_token_servidor), 
    db: Session = Depends(get_db)
):
    # Extraemos la IP real desde donde el agente está mandando los datos
    ip_real = request.client.host

    # 🌟 NUEVO: Actualizamos el estado a Online Y la IP si ha cambiado
    ha_cambiado = False
    if servidor.estado != "Online":
        servidor.estado = "Online"
        ha_cambiado = True
        
    if servidor.ip_direccion != ip_real:
        servidor.ip_direccion = ip_real # Auto-actualizamos la IP
        ha_cambiado = True
        
    if ha_cambiado:
        db.commit()

    # 1. Guardamos la métrica en la base de datos
    crud_metrica.create_metrica(db=db, metrica=metrica, servidor_id=servidor.id)
    
    # 2. EVALUACIÓN DINÁMICA POR UMBRALES (A PRUEBA DE FALLOS)
    mensaje_alerta = None
    
    # Extraemos los umbrales de la BD o aplicamos defaults seguros
    umbral_cpu = servidor.umbral_cpu or 90.0
    umbral_ram = servidor.umbral_ram or 16000.0
    umbral_disco = servidor.umbral_disco or 90.0
    umbral_red = servidor.umbral_red or 500.0
    
    # Evaluamos asegurándonos de que la métrica tampoco sea nula
    if metrica.cpu_usage_pct is not None and metrica.cpu_usage_pct >= umbral_cpu:
        mensaje_alerta = f"Uso de CPU crítico: {metrica.cpu_usage_pct}% (Supera el umbral de {umbral_cpu}%)"
        
    elif metrica.ram_usage_mb is not None and metrica.ram_usage_mb >= umbral_ram:
        mensaje_alerta = f"Consumo de RAM elevado: {metrica.ram_usage_mb}MB (Supera el umbral de {umbral_ram}MB)"
        
    elif metrica.disk_usage_pct is not None and metrica.disk_usage_pct >= umbral_disco:
        mensaje_alerta = f"Espacio en disco casi lleno: {metrica.disk_usage_pct}% (Supera el umbral de {umbral_disco}%)"
        
    elif metrica.network_latency_ms is not None and metrica.network_latency_ms >= umbral_red:
        mensaje_alerta = f"Latencia de red inusual: {metrica.network_latency_ms}ms (Supera el umbral de {umbral_red}ms)"
        
    # 3. Guardar la alerta si se superó algún límite
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
        .order_by(MetricaHardware.tiempo.desc()) # Pillamos las MÁS RECIENTES
        .limit(limit)
        .all()
    )
    metricas.reverse() # Le damos la vuelta para que la gráfica avance hacia la derecha
    return metricas


@router.get("/", response_model=List[MetricaResponse])
def obtener_todas_las_metricas(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Recupera el historial global de todas las máquinas.
    """
    metricas = (
        db.query(MetricaHardware)
        .order_by(MetricaHardware.tiempo.desc()) # 🛠️ ¡AQUÍ ESTABA EL ERROR! Ahora es desc()
        .limit(limit)
        .all()
    )
    metricas.reverse() # Invertimos para orden cronológico correcto
    return metricas