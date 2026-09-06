import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Variable de entorno inyectada por Docker Compose; en local sin Docker,
# usa las credenciales por defecto para desarrollo
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://admin:password_segura@localhost:5432/sistema_it"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# expire_on_commit=False evita que los objetos queden invalidados tras un commit,
# lo cual es necesario para devolver objetos ORM directamente como respuesta de FastAPI
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

Base = declarative_base()


def get_db():
    """Dependencia de FastAPI que gestiona el ciclo de vida de una sesión de BD por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()