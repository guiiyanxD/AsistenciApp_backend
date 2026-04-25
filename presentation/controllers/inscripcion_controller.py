from business.services.inscripcion_service import InscripcionService
from presentation.middlewares.auth_middleware import solo_estudiante, autenticar
from utils.http_helpers import read_json_body, send_json, send_error

inscripcion_service = InscripcionService()


def handle_inscripciones(handler, method: str, parts: list[str]):
    """
    POST /api/inscripciones/unirse          → estudiante se une con código
    GET  /api/inscripciones/mis-grupos      → grupos del estudiante autenticado
    """
    accion = parts[2] if len(parts) >= 3 else None

    if method == "POST" and accion == "unirse":
        _unirse(handler)
    elif method == "GET" and accion == "mis-grupos":
        _mis_grupos(handler)
    else:
        send_error(handler, 404, "Ruta no encontrada")


def _unirse(handler):
    payload = solo_estudiante(handler)
    if not payload:
        return
    try:
        body = read_json_body(handler)
        codigo = body.get("codigo", "")
        resultado = inscripcion_service.unirse_por_codigo(
            codigo, payload["sub"]
        )
        send_json(handler, 201, resultado)
    except LookupError as e:
        send_error(handler, 404, str(e))
    except ValueError as e:
        send_error(handler, 400, str(e))
    except Exception:
        send_error(handler, 500, "Error interno del servidor")


def _mis_grupos(handler):
    payload = solo_estudiante(handler)
    if not payload:
        return
    try:
        grupos = inscripcion_service.listar_grupos_estudiante(payload["sub"])
        send_json(handler, 200, {"grupos": grupos})
    except Exception:
        send_error(handler, 500, "Error interno del servidor")
