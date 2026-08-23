import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Leemos la variable de entorno que inyecta Docker. 
# Si no existe (porque lo ejecutas en local fuera de Docker), 
# apunta automáticamente a tus credenciales locales correctas.
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://admin:password_segura@localhost:5432/sistema_it"
)

# El 'engine' es el motor que gestiona la comunicación real con PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal para abrir sesiones temporales con la BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base es la clase madre de la que heredarán todos tus modelos
Base = declarative_base()

# Dependencia para que FastAPI abra y cierre la conexión automáticamente
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()