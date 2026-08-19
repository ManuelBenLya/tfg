from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "API Monitorización TFG"
    
    # Base de datos
    DATABASE_URL: str = "postgresql://admin:password_segura@localhost:5432/sistema_it"
    
    # Seguridad JWT
    SECRET_KEY: str = "361805ca69f70407baeda08083407154c55af50a705c907cf941f4c714ac0cae"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Le decimos que intente leer estas variables de un archivo .env
    model_config = SettingsConfigDict(env_file=".env")

# Instanciamos la configuración para poder importarla desde cualquier parte
settings = Settings()