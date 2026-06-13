from business.grupo_business import GrupoBusiness
from presentation.middlewares.auth_middleware import solo_docente
from utils.http_helpers import read_json_body, send_json, send_error

grupo_business = GrupoBusiness()


def handle_grupos(handler, method: str, parts: list[str]):
    """
    GET    /api/grupos                        → listar grupos del docente
    POST   /api/grupos                        → crear grupo con horarios
    GET    /api/grupos/{id}                   → obtener grupo
    GET    /api/grupos/{id}/clases            → listar clases generadas
    PUT    /api/grupos/{id}/horarios          → regenerar horarios y clases
    """
    payload = solo_docente(handler)
    if not payload:
        return

    docente_id = payload["sub"]
    grupo_id = parts[2] if len(parts) >= 3 and parts[2] else None
    subrecurso = parts[3] if len(parts) >= 4 else None

    try:
        if method == "GET" and not grupo_id:
            grupos = grupo_business.listar(docente_id)
            send_json(handler, 200, {"grupos": grupos})

        elif method == "POST" and not grupo_id:
            body = read_json_body(handler)
            grupo = grupo_business.crear(
                docente_id,
                body.get("periodo_id", ""),
                body.get("materia_id", ""),
                body.get("nombre", ""),
                body.get("cupo_maximo"),
                body.get("horarios", []),
            )
            send_json(handler, 201, grupo)

        elif method == "GET" and grupo_id and not subrecurso:
            grupo = grupo_business.obtener(grupo_id, docente_id)
            send_json(handler, 200, grupo)

        elif method == "GET" and grupo_id and subrecurso == "clases":
            clases = grupo_business.listar_clases(grupo_id, docente_id)
            send_json(handler, 200, {"clases": clases, "total": len(clases)})

        elif method == "PUT" and grupo_id and subrecurso == "horarios":
            body = read_json_body(handler)
            resultado = grupo_business.regenerar_clases(
                grupo_id, docente_id, body.get("horarios", [])
            )
            send_json(handler, 200, resultado)

        else:
            send_error(handler, 404, "Ruta no encontrada")

    except LookupError as e:
        send_error(handler, 404, str(e))
    except ValueError as e:
        send_error(handler, 400, str(e))
    except Exception:
        send_error(handler, 500, "Error interno del servidor")
