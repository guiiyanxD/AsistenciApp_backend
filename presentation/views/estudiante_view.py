from business.inscripcion_business import InscripcionBusiness
from presentation.middlewares.auth_middleware import solo_estudiante_web
from utils.http_helpers import send_html, send_error, send_redirect, render_template, read_form_body

inscripcion_business = InscripcionBusiness()


def handle_estudiante_web(handler, method: str, partes: list):
    payload = solo_estudiante_web(handler)
    if not payload:
        return

    seccion = partes[1] if len(partes) >= 2 else "inicio"

    if seccion == "inicio" and method == "GET":
        _inicio(handler, payload)
    elif seccion == "unirse" and method == "POST":
        _unirse(handler, payload)
    else:
        send_error(handler, 404, "Página no encontrada")


def _inicio(handler, payload: dict, error: str = None, codigo: str = ""):
    estudiante_id = payload["sub"]
    nombre        = payload.get("nombre", "Estudiante")
    try:
        grupos = inscripcion_business.listar_grupos_estudiante(estudiante_id)
        html = render_template(
            "estudiante/inicio.html",
            nombre=nombre,
            grupos=grupos,
            error=error,
            codigo=codigo,
        )
        send_html(handler, 200, html)
    except Exception as e:
        send_error(handler, 500, f"Error al cargar el panel: {str(e)}")


def _unirse(handler, payload: dict):
    body   = read_form_body(handler)
    codigo = body.get("codigo", "").strip()
    try:
        inscripcion_business.unirse_por_codigo(codigo, payload["sub"])
        send_redirect(handler, "/estudiante/inicio")
    except (ValueError, LookupError) as e:
        _inicio(handler, payload, error=str(e), codigo=codigo)
    except Exception:
        _inicio(handler, payload, error="Error interno del servidor.", codigo=codigo)
