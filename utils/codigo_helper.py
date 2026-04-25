import random
import string


def generar_codigo_invitacion(longitud: int = 8) -> str:
    caracteres = string.ascii_uppercase + string.digits
    return "".join(random.choices(caracteres, k=longitud))
