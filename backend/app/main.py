from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import usuarios, servidores, metricas, alertas
app = FastAPI(
    title="API de Monitorización de Infraestructura",
    description="Backend centralizado para la gestión de servidores y métricas de hardware.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Unificamos todos los routers añadiendo su prefijo limpio y ordenado
app.include_router(
    usuarios.router, prefix="/api/usuarios", tags=["Usuarios"]
)
app.include_router(
    servidores.router, prefix="/api/servidores", tags=["Servidores"]
)
app.include_router(metricas.router, prefix="/api/metricas", tags=["Métricas"])

app.include_router(alertas.router, prefix="/api/alertas", tags=["Alertas"])

@app.get("/health", tags=["Sistema"])
def health_check():
    return {"estado": "operativo", "mensaje": "Servidor de monitorización activo"}