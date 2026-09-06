import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Table, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

# -------------------------------------------------------------------
# TABLA INTERMEDIA (Asignación granular dentro de la misma empresa)
# -------------------------------------------------------------------
usuario_servidor = Table(
    "usuario_servidor",
    Base.metadata,
    Column("usuario_id", UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
    Column("servidor_id", UUID(as_uuid=True), ForeignKey("servidores.id", ondelete="CASCADE"), primary_key=True),
)

# -------------------------------------------------------------------
# MODELO: EMPRESA (Tenant)
# -------------------------------------------------------------------
class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String, unique=True, nullable=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

    # Ajustes SMTP personalizados por empresa (Multi-tenant SMTP)
    smtp_host = Column(String, nullable=True)
    smtp_port = Column(Integer, nullable=True)
    smtp_user = Column(String, nullable=True)
    smtp_password = Column(String, nullable=True)
    smtp_from = Column(String, nullable=True)

    # Relaciones: Si borramos una empresa, se borran sus usuarios y servidores en cascada
    usuarios = relationship("Usuario", back_populates="empresa", cascade="all, delete-orphan")
    servidores = relationship("Servidor", back_populates="empresa", cascade="all, delete-orphan")

# -------------------------------------------------------------------
# MODELO: USUARIOS
# -------------------------------------------------------------------
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(String, default="usuario") # Roles: "admin" o "usuario"
    discord_webhook = Column(String, nullable=True)
    slack_webhook = Column(String, nullable=True)
    recibir_alertas_email = Column(Boolean, default=True)

    empresa = relationship("Empresa", back_populates="usuarios")
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
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String, nullable=False)
    ip_direccion = Column(String, nullable=False)
    token_auth = Column(String, unique=True, nullable=False)
    estado = Column(String, nullable=False, default="Offline")

    # Umbrales personalizables
    umbral_cpu = Column(Float, default=90.0)
    umbral_ram = Column(Float, default=16000.0) 
    umbral_disco = Column(Float, default=90.0)
    umbral_red = Column(Float, default=500.0)

    empresa = relationship("Empresa", back_populates="servidores")
    usuarios_con_acceso = relationship("Usuario", secondary=usuario_servidor, back_populates="servidores_supervisados")
    metricas = relationship("MetricaHardware", back_populates="servidor", cascade="all, delete-orphan")
    alertas = relationship("Alerta", back_populates="servidor", cascade="all, delete-orphan")

# -------------------------------------------------------------------
# MODELO: METRICAS_HARDWARE
# -------------------------------------------------------------------
class MetricaHardware(Base):
    __tablename__ = "metricas_hardware"

    tiempo = Column(DateTime, primary_key=True)
    servidor_id = Column(UUID(as_uuid=True), ForeignKey("servidores.id", ondelete="CASCADE"), primary_key=True)
    
    cpu_usage_pct = Column(Float)
    ram_usage_mb = Column(Float)
    disk_usage_pct = Column(Float)
    disk_os_gb = Column(Float, default=0.0)
    disk_db_gb = Column(Float, default=0.0)
    disk_logs_gb = Column(Float, default=0.0)
    disk_free_gb = Column(Float, default=0.0)
    network_latency_ms = Column(Float)
    discos_json = Column(JSON, nullable=True)

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