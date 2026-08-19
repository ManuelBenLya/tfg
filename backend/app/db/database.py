from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# URL de conexión a tu base de datos local (PostgreSQL en Docker)
# Nota: Apuntamos a localhost en el puerto 5432 porque tu código 
# Python se está ejecutando desde tu máquina anfitriona.
SQLALCHEMY_DATABASE_URL = "postgresql://admin:password_segura@localhost:5432/sistema_it"

# El 'engine' es el motor que gestiona la comunicación real con PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal es la fábrica de sesiones. Cada vez que llegue una petición 
# a tu API, usaremos esto para abrir una conversación temporal con la BD.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base es la clase madre de la que heredarán todos tus modelos (Usuarios, Servidores...)
Base = declarative_base()

# Dependencia para que FastAPI abra y cierre la conexión automáticamente
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()