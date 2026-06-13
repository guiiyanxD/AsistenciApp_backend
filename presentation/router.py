from urllib.parse import urlparse
from presentation.views.auth_view import handle_auth_web
from presentation.views.docente_view import handle_docente_web
from presentation.views.estudiante_view import handle_estudiante_web
from presentation.views.admin_view import handle_admin_web
from utils.http_helpers import send_error, send_redirect, serve_static


def enrutar(handler, method: str, path: str):
    parsed = urlparse(path)
    partes = [p for p in parsed.path.split("/") if p]

    if not partes:
        send_redirect(handler, "/login")
        return

    primera = partes[0]

    if primera == "static":
        serve_static(handler, parsed.path)
        return

    if primera in ("login", "logout", "registro"):
        handle_auth_web(handler, method, partes)
        return

    if primera == "docente":
        handle_docente_web(handler, method, partes)
        return

    if primera == "estudiante":
        handle_estudiante_web(handler, method, partes)
        return

    if primera == "admin":
        handle_admin_web(handler, method, partes)
        return

    send_error(handler, 404, "Ruta no encontrada")
