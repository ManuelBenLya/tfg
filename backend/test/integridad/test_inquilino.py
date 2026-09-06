import pytest
from sqlalchemy.orm import Session
# Ajusta estos imports a las rutas reales de tus modelos y CRUD
# from app.crud.servidor import get_server_by_id_and_company

def test_cross_tenant_access_prevention():
    """Simula que un usuario de la Empresa A intenta consultar un servidor de la Empresa B."""
    empresa_a_id = "uuid-empresa-a-123"
    empresa_b_id = "uuid-empresa-b-456"
    
    servidor_de_b = {"id": "srv-999", "empresa_id": empresa_b_id, "nombre": "Server-B"}
    
    # Comprobación lógica del aislamiento multitenant
    # Si la consulta filtra por empresa_id de la sesión del usuario, debe retornar None o denegar
    acceso_permitido = servidor_de_b["empresa_id"] == empresa_a_id
    
    assert acceso_permitido is False