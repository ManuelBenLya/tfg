import secrets
from app.core.security import get_password_hash, verify_password

def test_password_hashing():
    """Valida que el hash se genere correctamente y la contraseña sea verificable."""
    password = "MiPasswordSeguro123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("PasswordFalso", hashed) is False

def test_agent_token_generation():
    """Valida que el token de 32 bytes para agentes tenga la entropía adecuada."""
    token = secrets.token_urlsafe(32)
    # Un token urlsafe de 32 bytes suele generar una cadena de longitud aproximada a 43 caracteres
    assert isinstance(token, str)
    assert len(token) >= 40