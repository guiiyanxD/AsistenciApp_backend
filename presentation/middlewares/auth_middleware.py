import jwt
from utils.jwt_helper import verificar_token
from utils.http_helpers import send_redirect


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


def solo_admin_web(handler) -> dict | None:
    payload = autenticar_web(handler)
    if payload is None:
        return None
    if payload.get("rol") != "admin":
        send_redirect(handler, "/login")
        return None
    return payload
