from urllib.parse import urlparse
from presentation.controllers.auth_controller import handle_auth
from presentation.controllers.materia_controller import handle_materias
from presentation.controllers.periodo_controller import handle_periodos
from presentation.controllers.grupo_controller import handle_grupos
from presentation.controllers.inscripcion_controller import handle_inscripciones
from presentation.controllers.asistencia_controller import handle_asistencias
from presentation.controllers.clase_controller import handle_clases, handle_clases_grupo
from utils.http_helpers import send_json, send_error


def enrutar(handler, method: str, path: str):
    parsed = urlparse(path)
    # Normalizar: quitar trailing slash y dividir
    partes = [p for p in parsed.path.split("/") if p]
    # partes[0] = "api", partes[1] = recurso, partes[2] = id (opcional), ...

    if not partes or partes[0] != "api":
        send_error(handler, 404, "Ruta no encontrada")
        return

    if len(partes) < 2:
        send_error(handler, 404, "Ruta no encontrada")
        return

    recurso = partes[1]

    # Manejar preflight CORS
    if method == "OPTIONS":
        handler.send_response(204)
        handler.send_header("Access-Control-Allow-Origin", "*")
        handler.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        handler.end_headers()
        return

    # Health check
    if recurso == "health" and method == "GET":
        send_json(handler, 200, {"status": "ok"})
        return
    
    if recurso == "grupos" and len(partes) >= 4 and partes[3] == "clases":
        if method == "POST":
            handle_clases_grupo(handler, method, partes)
        else:
            handle_grupos(handler, method, partes)
        return

    # Despachar a controladores
    rutas = {
        "auth":          handle_auth,
        "materias":      handle_materias,
        "periodos":      handle_periodos,
        "grupos":        handle_grupos,
        "inscripciones": handle_inscripciones,
        "asistencias":   handle_asistencias,
        "clases":        handle_clases,
    }

    if recurso in rutas:
        rutas[recurso](handler, method, partes)
    else:
        send_error(handler, 404, f"Recurso '{recurso}' no encontrado")
