import jwt
from utils.jwt_helper import verificar_token
from utils.http_helpers import send_error


def autenticar(handler) -> dict | None:
    # Imprimir TODOS los headers para ver qué envía Flutter realmente
    print("=== HEADERS RECIBIDOS ===")
    print(handler.headers) 
    print("=========================")
    auth_header = handler.headers.get("Authorization", "")
    print("log de prueba desde autenticar")  # Debug: Verificar el contenido del header
    if not auth_header.startswith("Bearer "):
        send_error(handler, 401, "Token de autenticacion requerido ")
        return None
    
    token = auth_header.split(" ", 1)[1]
    try:
        return verificar_token(token)
    except jwt.ExpiredSignatureError:
        send_error(handler, 401, "Token expirado")
        return None
    except jwt.InvalidTokenError:
        send_error(handler, 401, "Token invalido")
        return None
    


def solo_docente(handler) -> dict | None:
    payload = autenticar(handler)
    if payload is None:
        return None
    if payload.get("rol") != "docente":
        send_error(handler, 403, "Acceso restringido a docentes")
        return None
    return payload


def solo_estudiante(handler) -> dict | None:
    payload = autenticar(handler)
    if payload is None:
        return None
    if payload.get("rol") != "estudiante":
        send_error(handler, 403, "Acceso restringido a estudiantes")
        return None
    return payload
