from business.inscripcion_business import InscripcionBusiness
from presentation.middlewares.auth_middleware import solo_estudiante_web
from utils.http_helpers import send_html, send_error, render_template

inscripcion_business = InscripcionBusiness()


def handle_estudiante_web(handler, method: str, partes: list):
    payload = solo_estudiante_web(handler)
    if not payload:
        return

    seccion = partes[1] if len(partes) >= 2 else "inicio"

    if method == "GET" and seccion == "inicio":
        _inicio(handler, payload)
    else:
        send_error(handler, 404, "Página no encontrada")


def _inicio(handler, payload: dict):
    estudiante_id = payload["sub"]
    nombre        = payload.get("nombre", "Estudiante")

    try:
        grupos = inscripcion_business.listar_grupos_estudiante(estudiante_id)

        html = render_template(
            "estudiante/inicio.html",
            nombre=nombre,
            grupos=grupos,
        )
        send_html(handler, 200, html)
    except Exception as e:
        send_error(handler, 500, f"Error al cargar el panel: {str(e)}")
