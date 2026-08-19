import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Table, Float
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

# -------------------------------------------------------------------
# TABLA INTERMEDIA
# -------------------------------------------------------------------
usuario_servidor = Table(
    "usuario_servidor",
    Base.metadata,
    Column("usuario_id", UUID(as_uuid=True), ForeignKey("usuarios.id"), primary_key=True),
    Column("servidor_id", UUID(as_uuid=True), ForeignKey("servidores.id"), primary_key=True),
)

# -------------------------------------------------------------------
# MODELO: USUARIOS
# -------------------------------------------------------------------
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(String, nullable=False)

    servidores_supervisados = relationship(
        "Servidor", 
        secondary=usuario_servidor, 
        back_populates="usuarios_con_acceso"
    )

# -------------------------------------------------------------------
# MODELO: SERVIDORES
# -------------------------------------------------------------------
class Servidor(Base):
    __tablename__ = "servidores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String, nullable=False)
    ip_direccion = Column(String, nullable=False)
    token_auth = Column(String, unique=True, nullable=False)
    estado = Column(String, nullable=False)

    # Umbrales personalizables
    umbral_cpu = Column(Float, default=90.0)
    umbral_ram = Column(Float, default=16000.0) 
    umbral_disco = Column(Float, default=90.0)
    umbral_red = Column(Float, default=500.0)

    usuarios_con_acceso = relationship("Usuario", secondary=usuario_servidor, back_populates="servidores_supervisados")
    metricas = relationship("MetricaHardware", back_populates="servidor")
    alertas = relationship("Alerta", back_populates="servidor", cascade="all, delete-orphan")

# -------------------------------------------------------------------
# MODELO: METRICAS_HARDWARE
# -------------------------------------------------------------------
class MetricaHardware(Base):
    __tablename__ = "metricas_hardware"

    tiempo = Column(DateTime, primary_key=True)
    servidor_id = Column(UUID(as_uuid=True), ForeignKey("servidores.id"), primary_key=True)
    
    cpu_usage_pct = Column(Float)
    ram_usage_mb = Column(Float)
    disk_usage_pct = Column(Float)
    network_latency_ms = Column(Float)

    servidor = relationship("Servidor", back_populates="metricas")

# -------------------------------------------------------------------
# MODELO: ALERTAS
# -------------------------------------------------------------------
class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    servidor_id = Column(UUID(as_uuid=True), ForeignKey("servidores.id", ondelete="CASCADE"), index=True)
    mensaje = Column(String, nullable=False)
    leida = Column(Boolean, default=False)
    tiempo = Column(DateTime(timezone=True), server_default=func.now())

    servidor = relationship("Servidor", back_populates="alertas")