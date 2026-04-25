from business.services.auth_service import AuthService
from utils.http_helpers import read_json_body, send_json, send_error

auth_service = AuthService()


def handle_auth(handler, method: str, parts: list[str]):
    if len(parts) < 3:
        send_error(handler, 404, "Ruta no encontrada")
        return

    accion = parts[2]

    if method == "POST" and accion == "registro-docente":
        _registrar_docente(handler)
    elif method == "POST" and accion == "login-docente":
        _login_docente(handler)
    elif method == "POST" and accion == "registro-estudiante":
        _registrar_estudiante(handler)
    elif method == "POST" and accion == "login-estudiante":
        _login_estudiante(handler)
    else:
        send_error(handler, 404, "Ruta de autenticación no encontrada")


def _registrar_docente(handler):
    try:
        body = read_json_body(handler)
        resultado = auth_service.registrar_docente(
            body.get("nombre", ""),
            body.get("email", ""),
            body.get("password", ""),
            body.get("profesion", "")
        )
        send_json(handler, 201, resultado)
    except ValueError as e:
        send_error(handler, 400, str(e))
    except Exception:
        send_error(handler, 500, "Error interno del servidor")


def _login_docente(handler):
    try:
        body = read_json_body(handler)
        resultado = auth_service.login_docente(
            body.get("email", ""),
            body.get("password", ""),
        )
        send_json(handler, 200, resultado)
    except ValueError as e:
        send_error(handler, 400, str(e))
    except PermissionError as e:
        send_error(handler, 401, str(e))
    except Exception:
        send_error(handler, 500, "Error interno del servidor")


def _registrar_estudiante(handler):
    try:
        body = read_json_body(handler)
        resultado = auth_service.registrar_estudiante(
            body.get("nombre", ""),
            body.get("email", ""),
            body.get("password", ""),
        )
        send_json(handler, 201, resultado)
    except ValueError as e:
        send_error(handler, 400, str(e))
    except Exception:
        send_error(handler, 500, "Error interno del servidor")


def _login_estudiante(handler):
    try:
        body = read_json_body(handler)
        resultado = auth_service.login_estudiante(
            body.get("email", ""),
            body.get("password", ""),
        )
        send_json(handler, 200, resultado)
    except ValueError as e:
        send_error(handler, 400, str(e))
    except PermissionError as e:
        send_error(handler, 401, str(e))
    except Exception:
        send_error(handler, 500, "Error interno del servidor")
