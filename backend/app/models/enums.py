from enum import Enum


class RolUsuario(str, Enum):
    """
    Enum para los roles de usuario del sistema.
    Al heredar de str, se serializa correctamente en JSON y se compara con strings de la BD.
    """
    ADMIN = "admin"
    USUARIO = "usuario"
