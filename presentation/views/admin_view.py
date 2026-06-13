from presentation.middlewares.auth_middleware import solo_admin_web
from utils.http_helpers import send_html, send_error, render_template


def handle_admin_web(handler, method: str, partes: list):
    payload = solo_admin_web(handler)
    if not payload:
        return

    seccion = partes[1] if len(partes) >= 2 else "inicio"

    if method == "GET" and seccion == "inicio":
        _inicio(handler, payload)
    else:
        send_error(handler, 404, "Página no encontrada")


def _inicio(handler, payload: dict):
    nombre = payload.get("nombre", "Administrador")
    try:
        html = render_template("admin/inicio.html", nombre=nombre)
        send_html(handler, 200, html)
    except Exception as e:
        send_error(handler, 500, f"Error al cargar el panel: {str(e)}")
