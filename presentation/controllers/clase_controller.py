from business.clase_business import ClaseBusiness
from presentation.middlewares.auth_middleware import solo_docente
from utils.http_helpers import read_json_body, send_json, send_error

clase_business = ClaseBusiness()


def handle_clases(handler, method: str, parts: list[str]):
    """
    GET  /api/clases/{id}/asistencias   → asistencias en tiempo real
    PUT  /api/clases/{id}/tipo          → etiquetar clase
    PUT  /api/clases/{id}/cancelar      → cancelar clase
    PUT  /api/clases/{id}/restaurar     → restaurar clase cancelada
    """
    clase_id = parts[2] if len(parts) >= 3 else None
    accion   = parts[3] if len(parts) >= 4 else None

    if not clase_id:
        send_error(handler, 400, "clase_id es requerido")
        return

    if method == "GET" and accion == "asistencias":
        _asistencias(handler, clase_id)
    elif method == "PUT" and accion == "tipo":
        _cambiar_tipo(handler, clase_id)
    elif method == "PUT" and accion == "cancelar":
        _cancelar(handler, clase_id)
    elif method == "PUT" and accion == "restaurar":
        _restaurar(handler, clase_id)
    else:
        send_error(handler, 404, "Ruta no encontrada")


def handle_clases_grupo(handler, method: str, parts: list[str]):
    """
    POST /api/grupos/{id}/clases        → crear clase extraordinaria
    """
    grupo_id = parts[2] if len(parts) >= 3 else None

    if not grupo_id or method != "POST":
        send_error(handler, 404, "Ruta no encontrada")
        return

    _crear_extraordinaria(handler, grupo_id)


def _asistencias(handler, clase_id: str):
    payload = solo_docente(handler)
    if not payload:
        return
    try:
        resultado = clase_business.asistencias_clase(clase_id, payload["sub"])
        send_json(handler, 200, resultado)
    except LookupError as e:
        send_error(handler, 404, str(e))
    except PermissionError as e:
        send_error(handler, 403, str(e))
    except Exception:
        send_error(handler, 500, "Error interno del servidor")


def _cambiar_tipo(handler, clase_id: str):
    payload = solo_docente(handler)
    if not payload:
        return
    try:
        body = read_json_body(handler)
        tipo = body.get("tipo", "")
        if not tipo:
            send_error(handler, 400, "El campo 'tipo' es obligatorio")
            return
        actualizada = clase_business.cambiar_tipo(clase_id, payload["sub"], tipo)
        send_json(handler, 200, actualizada)
    except LookupError as e:
        send_error(handler, 404, str(e))
    except PermissionError as e:
        send_error(handler, 403, str(e))
    except ValueError as e:
        send_error(handler, 400, str(e))
    except Exception:
        send_error(handler, 500, "Error interno del servidor")


def _cancelar(handler, clase_id: str):
    payload = solo_docente(handler)
    if not payload:
        return
    try:
        body = read_json_body(handler)
        observaciones = body.get("observaciones", "")
        cancelada = clase_business.cancelar(clase_id, payload["sub"], observaciones)
        send_json(handler, 200, cancelada)
    except LookupError as e:
        send_error(handler, 404, str(e))
    except PermissionError as e:
        send_error(handler, 403, str(e))
    except ValueError as e:
        send_error(handler, 400, str(e))
    except Exception:
        send_error(handler, 500, "Error interno del servidor")


def _restaurar(handler, clase_id: str):
    payload = solo_docente(handler)
    if not payload:
        return
    try:
        restaurada = clase_business.restaurar(clase_id, payload["sub"])
        send_json(handler, 200, restaurada)
    except LookupError as e:
        send_error(handler, 404, str(e))
    except PermissionError as e:
        send_error(handler, 403, str(e))
    except ValueError as e:
        send_error(handler, 400, str(e))
    except Exception:
        send_error(handler, 500, "Error interno del servidor")


def _crear_extraordinaria(handler, grupo_id: str):
    payload = solo_docente(handler)
    if not payload:
        return
    try:
        body = read_json_body(handler)
        clase = clase_business.crear_extraordinaria(
            docente_id=payload["sub"],
            grupo_id=grupo_id,
            fecha=body.get("fecha", ""),
            hora_inicio=body.get("hora_inicio", ""),
            hora_fin=body.get("hora_fin", ""),
            tipo=body.get("tipo", "clase"),
            observaciones=body.get("observaciones"),
        )
        send_json(handler, 201, clase)
    except LookupError as e:
        send_error(handler, 404, str(e))
    except PermissionError as e:
        send_error(handler, 403, str(e))
    except ValueError as e:
        send_error(handler, 400, str(e))
    except Exception:
        send_error(handler, 500, "Error interno del servidor")
