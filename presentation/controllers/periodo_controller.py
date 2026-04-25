from business.services.periodo_service import PeriodoService
from presentation.middlewares.auth_middleware import solo_docente
from utils.http_helpers import read_json_body, send_json, send_error

periodo_service = PeriodoService()


def handle_periodos(handler, method: str, parts: list[str]):
    """
    GET    /api/periodos           → listar
    POST   /api/periodos           → crear
    GET    /api/periodos/{id}      → obtener
    PUT    /api/periodos/{id}      → actualizar
    DELETE /api/periodos/{id}      → eliminar
    """
    payload = solo_docente(handler)
    if not payload:
        return

    docente_id = payload["sub"]
    tiene_id = len(parts) >= 3 and parts[2]
    periodo_id = parts[2] if tiene_id else None

    try:
        if method == "GET" and not periodo_id:
            periodos = periodo_service.listar(docente_id)
            send_json(handler, 200, {"periodos": periodos})

        elif method == "GET" and periodo_id:
            periodo = periodo_service.obtener(periodo_id, docente_id)
            send_json(handler, 200, periodo)

        elif method == "POST" and not periodo_id:
            body = read_json_body(handler)
            periodo = periodo_service.crear(
                docente_id,
                body.get("nombre", ""),
                body.get("tipo", ""),
                body.get("fecha_inicio", ""),
                body.get("fecha_fin", ""),
            )
            send_json(handler, 201, periodo)

        elif method == "PUT" and periodo_id:
            body = read_json_body(handler)
            periodo = periodo_service.actualizar(
                periodo_id, docente_id,
                body.get("nombre", ""),
                body.get("tipo", ""),
                body.get("fecha_inicio", ""),
                body.get("fecha_fin", ""),
                body.get("activo", True),
            )
            send_json(handler, 200, periodo)

        elif method == "DELETE" and periodo_id:
            periodo_service.eliminar(periodo_id, docente_id)
            send_json(handler, 200, {"mensaje": "Periodo eliminado correctamente"})

        else:
            send_error(handler, 404, "Ruta no encontrada")

    except LookupError as e:
        send_error(handler, 404, str(e))
    except ValueError as e:
        send_error(handler, 400, str(e))
    except Exception:
        send_error(handler, 500, "Error interno del servidor")
