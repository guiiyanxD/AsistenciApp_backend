import jwt
from utils.jwt_helper import verificar_token
from utils.http_helpers import send_error, send_redirect


# ── Autenticación para la API móvil (Bearer token) ────────────────────────────

def autenticar(handler) -> dict | None:
    print("=== HEADERS RECIBIDOS ===")
    print(handler.headers)
    print("=========================")
    auth_header = handler.headers.get("Authorization", "")
    print("log de prueba desde autenticar")
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


# ── Autenticación para las vistas web (cookie de sesión) ─────────────────────

def _parse_cookie(header: str) -> dict:
    cookies = {}
    for parte in header.split(";"):
        parte = parte.strip()
        if "=" in parte:
            nombre, _, valor = parte.partition("=")
            cookies[nombre.strip()] = valor.strip()
    return cookies


def autenticar_web(handler) -> dict | None:
    cookie_header = handler.headers.get("Cookie", "")
    token = _parse_cookie(cookie_header).get("session")
    if not token:
        send_redirect(handler, "/login")
        return None
    try:
        return verificar_token(token)
    except jwt.ExpiredSignatureError:
        send_redirect(handler, "/login")
        return None
    except jwt.InvalidTokenError:
        send_redirect(handler, "/login")
        return None


def solo_docente_web(handler) -> dict | None:
    payload = autenticar_web(handler)
    if payload is None:
        return None
    if payload.get("rol") != "docente":
        send_redirect(handler, "/login")
        return None
    return payload


def solo_estudiante_web(handler) -> dict | None:
    payload = autenticar_web(handler)
    if payload is None:
        return None
    if payload.get("rol") != "estudiante":
        send_redirect(handler, "/login")
        return None
    return payload
