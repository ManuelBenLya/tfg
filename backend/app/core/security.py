from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext

# --- CONFIGURACIÓN JWT ---
# Recuerda poner aquí tu clave real generada con openssl
SECRET_KEY = "361805ca69f70407baeda08083407154c55af50a705c907cf941f4c714ac0cae" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- CONFIGURACIÓN BCRYPT ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- FUNCIONES DE CONTRASEÑAS ---
def get_password_hash(password: str) -> str:
    """Recibe una contraseña en texto plano, la recorta a 72 bytes por seguridad de bcrypt y devuelve su hash."""
    encoded_password = password.encode('utf-8')[:72]
    return pwd_context.hash(encoded_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con el hash guardado."""
    encoded_password = plain_password.encode('utf-8')[:72]
    return pwd_context.verify(encoded_password, hashed_password)

# --- FUNCIONES JWT ---
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Genera un JSON Web Token (JWT) firmado con un tiempo de expiración."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt