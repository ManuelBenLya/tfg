from app.db.database import engine, Base
from app.models import models

print("Conectando a la base de datos...")
# Borra todas las tablas registradas en los modelos
Base.metadata.drop_all(bind=engine)
print("¡Todas las tablas han sido borradas con éxito!")
