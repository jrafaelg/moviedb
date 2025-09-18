from enum import Enum


class JWTAction(Enum):
    NO_ACTION      = 0
    VALIDAR_EMAIL  = 1
    RESET_PASSWORD = 2
