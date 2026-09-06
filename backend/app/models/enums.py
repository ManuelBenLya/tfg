from enum import Enum


class RolUsuario(str, Enum):
    """
    Roles del sistema. Hereda de str para serialización directa a JSON
    y comparación transparente con los valores almacenados en PostgreSQL.
    """
    ADMIN = "admin"
    USUARIO = "usuario"
