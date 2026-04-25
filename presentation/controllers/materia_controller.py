from business.services.materia_service import MateriaService
from presentation.middlewares.auth_middleware import solo_docente
from utils.http_helpers import read_json_body, send_json, send_error

materia_service = MateriaService()


def handle_materias(handler, method: str, parts: list[str]):
    """
    GET    /api/materias           → listar
    POST   /api/materias           → crear
    GET    /api/materias/{id}      → obtener
    PUT    /api/materias/{id}      → actualizar
    DELETE /api/materias/{id}      → eliminar
    """
    payload = solo_docente(handler)
    if not payload:
        return

    docente_id = payload["sub"]
    tiene_id = len(parts) >= 3 and parts[2]
    materia_id = parts[2] if tiene_id else None

    try:
        if method == "GET" and not materia_id:
            materias = materia_service.listar(docente_id)
            send_json(handler, 200, {"materias": materias})

        elif method == "GET" and materia_id:
            materia = materia_service.obtener(materia_id, docente_id)
            send_json(handler, 200, materia)

        elif method == "POST" and not materia_id:
            body = read_json_body(handler)
            materia = materia_service.crear(
                docente_id,
                body.get("nombre", ""),
                body.get("codigo"),
                body.get("descripcion"),
            )
            send_json(handler, 201, materia)

        elif method == "PUT" and materia_id:
            body = read_json_body(handler)
            materia = materia_service.actualizar(
                materia_id, docente_id,
                body.get("nombre", ""),
                body.get("codigo"),
                body.get("descripcion"),
            )
            send_json(handler, 200, materia)

        elif method == "DELETE" and materia_id:
            materia_service.eliminar(materia_id, docente_id)
            send_json(handler, 200, {"mensaje": "Materia eliminada correctamente"})

        else:
            send_error(handler, 404, "Ruta no encontrada")

    except LookupError as e:
        send_error(handler, 404, str(e))
    except ValueError as e:
        send_error(handler, 400, str(e))
    except Exception:
        send_error(handler, 500, "Error interno del servidor")
