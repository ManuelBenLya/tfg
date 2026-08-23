from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.db.database import get_db
from app.schemas.servidor import ServidorCreate, ServidorResponse, UmbralesUpdate, ServidorUpdate
from app.crud import servidor as crud_servidor
from app.api.deps import get_current_user
from app.models.models import Usuario, Servidor, MetricaHardware
from fastapi.responses import StreamingResponse
from app.services.pdf_generator import crear_reporte_pdf

from pydantic import BaseModel
from uuid import UUID

router = APIRouter(tags=["Servidores"])


@router.post("/", response_model=ServidorResponse, status_code=status.HTTP_201_CREATED)
def crear_servidor(
    servidor: ServidorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Solo los ADMINISTRADORES pueden registrar un nuevo servidor.
    """
    # 1. Verificamos que sea admin
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para crear servidores.")

    # 2. 🌟 Pasamos el empresa_id al CRUD para que Postgres no se queje
    nuevo_servidor = crud_servidor.create_servidor(
        db=db, 
        servidor=servidor, 
        empresa_id=current_user.empresa_id
    )
    
    # 3. VINCULACIÓN AUTOMÁTICA: Añadimos al admin a la tabla intermedia
    nuevo_servidor.usuarios_con_acceso.append(current_user)
    db.commit()
    db.refresh(nuevo_servidor)
    
    return nuevo_servidor

    

@router.get("/", response_model=List[ServidorResponse])
def listar_servidores(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Devuelve SOLO los servidores a los que este usuario tiene acceso 
    (gracias a la tabla intermedia), y actualiza su estado.
    """
    # 🔒 REGLA 2: Visibilidad granular
    # En lugar de pedir todos al CRUD, sacamos solo los que tiene asignados este usuario
    servidores = current_user.servidores_supervisados
    
    limite_tiempo = datetime.utcnow() - timedelta(seconds=15)
    
    # Comprobación perezosa (Lazy Validation)
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
            
    db.commit()
    return servidores

@router.patch("/{servidor_id}/umbrales")
def actualizar_umbrales(
    servidor_id: str, 
    umbrales: UmbralesUpdate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user) # 🔒 Añadimos current_user
):
    """
    Solo un ADMINISTRADOR que tenga acceso a este servidor puede modificar umbrales.
    """
    # 🔒 REGLA 3: Solo admins modifican umbrales
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para modificar umbrales.")

    # Buscamos el servidor, comprobando que el admin realmente tiene acceso a él
    servidor = db.query(Servidor).filter(
        Servidor.id == servidor_id,
        Servidor.usuarios_con_acceso.any(id=current_user.id) # Magia de SQLAlchemy
    ).first()
    
    if not servidor:
        raise HTTPException(status_code=404, detail="Servidor no encontrado o sin acceso.")
        
    servidor.umbral_cpu = umbrales.umbral_cpu
    servidor.umbral_ram = umbrales.umbral_ram
    servidor.umbral_disco = umbrales.umbral_disco
    servidor.umbral_red = umbrales.umbral_red
    
    db.commit()
    return {"mensaje": "Umbrales actualizados correctamente"}



class AsignarUsuariosRequest(BaseModel):
    usuario_ids: List[UUID]

@router.post("/{servidor_id}/asignar-usuarios")
def asignar_usuarios_a_servidor(
    servidor_id: str,
    request: AsignarUsuariosRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Asigna qué usuarios pueden ver un servidor específico.
    """
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos.")

    # 1. Buscamos el servidor asegurándonos de que pertenece a la empresa del Admin
    servidor = db.query(Servidor).filter(
        Servidor.id == servidor_id,
        Servidor.empresa_id == current_user.empresa_id
    ).first()

    if not servidor:
        raise HTTPException(status_code=404, detail="Servidor no encontrado.")

    # 2. Buscamos a los usuarios que el admin quiere asignar (verificando que son de su empresa)
    usuarios_a_asignar = db.query(Usuario).filter(
        Usuario.id.in_(request.usuario_ids),
        Usuario.empresa_id == current_user.empresa_id
    ).all()

    # 3. 🌟 MAGIA DE SQLALCHEMY: Sobrescribimos la lista. 
    # SQLAlchemy borrará e insertará en la tabla 'usuario_servidor' automáticamente.
    servidor.usuarios_con_acceso = usuarios_a_asignar
    db.commit()

    return {"mensaje": "Accesos actualizados correctamente"}


@router.get("/{servidor_id}/reporte-pdf")
def descargar_reporte_pdf(
    servidor_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # 1. Buscamos el servidor y verificamos permisos (que sea de la empresa)
    servidor = db.query(Servidor).filter(
        Servidor.id == servidor_id,
        Servidor.empresa_id == current_user.empresa_id
    ).first()

    if not servidor:
        raise HTTPException(status_code=404, detail="Servidor no encontrado")

    # 2. Simulamos las métricas medias (aquí en el futuro consultarás tu tabla de métricas)
    # Por ahora le pasamos datos dummy para probar
    metricas_resumen = {
        "cpu_avg": 92.5,  # Forzamos un valor alto para que salte la regla del motor
        "ram_avg": 45.0,
        "disco_avg": 80.0
    }

    # 3. Generamos el PDF en memoria
    pdf_buffer = crear_reporte_pdf(servidor, metricas_resumen, current_user.email)

    # 4. Lo devolvemos al frontend como un archivo descargable
    headers = {
        'Content-Disposition': f'attachment; filename="Reporte_{servidor.nombre}.pdf"'
    }
    
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)



# -------------------------------------------------------------------
# EDITAR NOMBRE DEL SERVIDOR
# -------------------------------------------------------------------
@router.put("/{servidor_id}", status_code=status.HTTP_200_OK)
def actualizar_servidor(
    servidor_id: str,
    datos: ServidorUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para editar servidores.")
        
    servidor = db.query(Servidor).filter(Servidor.id == servidor_id, Servidor.empresa_id == current_user.empresa_id).first()
    if not servidor:
        raise HTTPException(status_code=404, detail="Servidor no encontrado.")
        
    servidor.nombre = datos.nombre
    db.commit()
    return {"mensaje": "Nombre del servidor actualizado correctamente."}

# -------------------------------------------------------------------
# ELIMINAR SERVIDOR (Y SUS MÉTRICAS)
# -------------------------------------------------------------------
@router.delete("/{servidor_id}", status_code=status.HTTP_200_OK)
def eliminar_servidor(
    servidor_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar servidores.")
        
    servidor = db.query(Servidor).filter(Servidor.id == servidor_id, Servidor.empresa_id == current_user.empresa_id).first()
    if not servidor:
        raise HTTPException(status_code=404, detail="Servidor no encontrado.")
        
    db.delete(servidor)
    db.commit()
    return {"mensaje": "Servidor y todas sus métricas eliminados correctamente."}