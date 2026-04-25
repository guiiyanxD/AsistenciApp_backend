from business.services.asistencia_service import AsistenciaService
from presentation.middlewares.auth_middleware import solo_estudiante, solo_docente
from utils.http_helpers import read_json_body, send_json, send_error

asistencia_service = AsistenciaService()


def handle_asistencias(handler, method: str, parts: list[str]):
    """
    POST /api/asistencias/marcar                          → estudiante marca asistencia
    GET  /api/asistencias/clase/{clase_id}                → docente ve asistencias de una clase
    GET  /api/asistencias/grupo/{grupo_id}/resumen        → docente ve resumen del grupo
    GET  /api/asistencias/grupo/{grupo_id}/mi-historial   → estudiante ve su historial
    """
    accion = parts[2] if len(parts) >= 3 else None
    sub_id = parts[3] if len(parts) >= 4 else None
    sub_accion = parts[4] if len(parts) >= 5 else None

    if method == "POST" and accion == "marcar":
        _marcar(handler)

    elif method == "GET" and accion == "clase" and sub_id:
        _por_clase(handler, sub_id)

    elif method == "GET" and accion == "grupo" and sub_id and sub_accion == "resumen":
        _resumen_grupo(handler, sub_id)

    elif method == "GET" and accion == "grupo" and sub_id and sub_accion == "mi-historial":
        _mi_historial(handler, sub_id)

    else:
        send_error(handler, 404, "Ruta no encontrada")


def _marcar(handler):
    payload = solo_estudiante(handler)
    if not payload:
        return
    try:
        body = read_json_body(handler)
        grupo_id = body.get("grupo_id", "")
        if not grupo_id:
            send_error(handler, 400, "grupo_id es obligatorio")
            return

        resultado = asistencia_service.marcar(
            estudiante_id=payload["sub"],
            grupo_id=grupo_id,
            latitud=body.get("latitud"),
            longitud=body.get("longitud"),
            precision_metros=body.get("precision_metros"),
        )
        send_json(handler, 201, resultado)
    except PermissionError as e:
        send_error(handler, 403, str(e))
    except ValueError as e:
        send_error(handler, 400, str(e))
    except Exception:
        send_error(handler, 500, "Error interno del servidor")


def _por_clase(handler, clase_id: str):
    payload = solo_docente(handler)
    if not payload:
        return
    try:
        asistencias = asistencia_service.listar_por_clase(clase_id, payload["sub"])
        send_json(handler, 200, {"asistencias": asistencias, "total": len(asistencias)})
    except LookupError as e:
        send_error(handler, 404, str(e))
    except PermissionError as e:
        send_error(handler, 403, str(e))
    except Exception:
        send_error(handler, 500, "Error interno del servidor")


def _resumen_grupo(handler, grupo_id: str):
    payload = solo_docente(handler)
    if not payload:
        return
    try:
        resumen = asistencia_service.resumen_por_grupo(grupo_id, payload["sub"])
        send_json(handler, 200, {"resumen": resumen})
    except PermissionError as e:
        send_error(handler, 403, str(e))
    except Exception:
        send_error(handler, 500, "Error interno del servidor")


def _mi_historial(handler, grupo_id: str):
    payload = solo_estudiante(handler)
    if not payload:
        return
    try:
        historial = asistencia_service.historial_estudiante(
            grupo_id, payload["sub"]
        )
        send_json(handler, 200, {"historial": historial})
    except PermissionError as e:
        send_error(handler, 403, str(e))
    except Exception:
        send_error(handler, 500, "Error interno del servidor")
