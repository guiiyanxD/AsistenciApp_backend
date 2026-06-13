from business.materia_business import MateriaBusiness
from business.periodo_business import PeriodoBusiness
from business.grupo_business import GrupoBusiness
from presentation.middlewares.auth_middleware import solo_docente_web
from utils.http_helpers import send_html, send_error, render_template

materia_business = MateriaBusiness()
periodo_business = PeriodoBusiness()
grupo_business   = GrupoBusiness()


def handle_docente_web(handler, method: str, partes: list):
    payload = solo_docente_web(handler)
    if not payload:
        return

    seccion = partes[1] if len(partes) >= 2 else "inicio"

    if method == "GET" and seccion == "inicio":
        _inicio(handler, payload)
    else:
        send_error(handler, 404, "Página no encontrada")


def _inicio(handler, payload: dict):
    docente_id = payload["sub"]
    nombre     = payload.get("nombre", "Docente")

    try:
        materias = materia_business.listar(docente_id)
        periodos = periodo_business.listar(docente_id)
        grupos   = grupo_business.listar(docente_id)

        html = render_template(
            "docente/inicio.html",
            nombre=nombre,
            materias=materias,
            periodos=periodos,
            grupos=grupos,
        )
        send_html(handler, 200, html)
    except Exception as e:
        send_error(handler, 500, f"Error al cargar el panel: {str(e)}")
