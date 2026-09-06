from app.db.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS alembic_version;"))
    conn.commit()
print("¡Memoria de Alembic borrada con éxito!")
