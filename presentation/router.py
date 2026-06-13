from urllib.parse import urlparse
from presentation.controllers.auth_controller import handle_auth
from presentation.controllers.materia_controller import handle_materias
from presentation.controllers.periodo_controller import handle_periodos
from presentation.controllers.grupo_controller import handle_grupos
from presentation.controllers.inscripcion_controller import handle_inscripciones
from presentation.controllers.asistencia_controller import handle_asistencias
from presentation.controllers.clase_controller import handle_clases, handle_clases_grupo
from presentation.views.auth_view import handle_auth_web
from presentation.views.docente_view import handle_docente_web
from presentation.views.estudiante_view import handle_estudiante_web
from utils.http_helpers import send_json, send_error, send_redirect, serve_static


def enrutar(handler, method: str, path: str):
    parsed = urlparse(path)
    partes = [p for p in parsed.path.split("/") if p]

    # Preflight CORS — solo aplica a las rutas de la API
    if method == "OPTIONS":
        handler.send_response(204)
        handler.send_header("Access-Control-Allow-Origin", "*")
        handler.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        handler.end_headers()
        return

    # Ruta raíz → redirigir al login web
    if not partes:
        send_redirect(handler, "/login")
        return

    primera = partes[0]

    # ── API JSON (app móvil) ──────────────────────────────────────────────────
    if primera == "api":
        _enrutar_api(handler, method, partes)
        return

    # ── Archivos estáticos ────────────────────────────────────────────────────
    if primera == "static":
        serve_static(handler, parsed.path)
        return

    # ── Vistas web ────────────────────────────────────────────────────────────
    if primera in ("login", "logout", "registro"):
        handle_auth_web(handler, method, partes)
        return

    if primera == "docente":
        handle_docente_web(handler, method, partes)
        return

    if primera == "estudiante":
        handle_estudiante_web(handler, method, partes)
        return

    send_error(handler, 404, "Ruta no encontrada")


def _enrutar_api(handler, method: str, partes: list):
    if len(partes) < 2:
        send_error(handler, 404, "Ruta no encontrada")
        return

    recurso = partes[1]

    if recurso == "health" and method == "GET":
        send_json(handler, 200, {"status": "ok"})
        return

    if recurso == "grupos" and len(partes) >= 4 and partes[3] == "clases":
        if method == "POST":
            handle_clases_grupo(handler, method, partes)
        else:
            handle_grupos(handler, method, partes)
        return

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
