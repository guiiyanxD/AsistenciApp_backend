from business.materia_business import MateriaBusiness
from business.periodo_business import PeriodoBusiness
from business.grupo_business import GrupoBusiness
from business.inscripcion_business import InscripcionBusiness
from presentation.middlewares.auth_middleware import solo_docente_web
from utils.http_helpers import send_html, send_error, send_redirect, render_template, read_form_body

materia_business     = MateriaBusiness()
periodo_business     = PeriodoBusiness()
grupo_business       = GrupoBusiness()
inscripcion_business = InscripcionBusiness()

_ACCIONES = {
    "aprobar":  inscripcion_business.aprobar,
    "reprobar": inscripcion_business.reprobar,
    "retirar":  inscripcion_business.retirar,
}


def handle_docente_web(handler, method: str, partes: list):
    payload = solo_docente_web(handler)
    if not payload:
        return

    seccion = partes[1] if len(partes) >= 2 else "inicio"

    if seccion == "inicio" and method == "GET":
        _inicio(handler, payload)

    elif seccion == "materias" and len(partes) >= 3 and partes[2] == "nueva":
        _form_materia(handler, method, payload)

    elif seccion == "periodos" and len(partes) >= 3 and partes[2] == "nuevo":
        _form_periodo(handler, method, payload)

    elif seccion == "grupos" and len(partes) >= 3 and partes[2] == "nuevo":
        _form_grupo(handler, method, payload)

    elif seccion == "grupos" and len(partes) >= 4 and partes[3] == "inscripciones":
        _listar_inscripciones(handler, partes[2])

    elif seccion == "inscripciones" and len(partes) >= 4:
        _accion_inscripcion(handler, method, partes[2], partes[3])

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


def _form_materia(handler, method: str, payload: dict):
    docente_id = payload["sub"]
    if method == "GET":
        html = render_template("docente/materia_form.html", error=None, valores={})
        send_html(handler, 200, html)
    elif method == "POST":
        body        = read_form_body(handler)
        nombre      = body.get("nombre", "").strip()
        codigo      = body.get("codigo", "").strip() or None
        descripcion = body.get("descripcion", "").strip() or None
        try:
            materia_business.crear(docente_id, nombre, codigo, descripcion)
            send_redirect(handler, "/docente/inicio")
        except (ValueError, LookupError) as e:
            html = render_template("docente/materia_form.html", error=str(e), valores=body)
            send_html(handler, 400, html)
    else:
        send_error(handler, 405, "Método no permitido")


def _form_periodo(handler, method: str, payload: dict):
    docente_id = payload["sub"]
    if method == "GET":
        html = render_template("docente/periodo_form.html", error=None, valores={})
        send_html(handler, 200, html)
    elif method == "POST":
        body         = read_form_body(handler)
        nombre       = body.get("nombre", "").strip()
        tipo         = body.get("tipo", "").strip()
        fecha_inicio = body.get("fecha_inicio", "").strip()
        fecha_fin    = body.get("fecha_fin", "").strip()
        try:
            periodo_business.crear(docente_id, nombre, tipo, fecha_inicio, fecha_fin)
            send_redirect(handler, "/docente/inicio")
        except (ValueError, LookupError) as e:
            html = render_template("docente/periodo_form.html", error=str(e), valores=body)
            send_html(handler, 400, html)
    else:
        send_error(handler, 405, "Método no permitido")


def _form_grupo(handler, method: str, payload: dict):
    docente_id = payload["sub"]
    if method == "GET":
        materias = materia_business.listar(docente_id)
        periodos = periodo_business.listar(docente_id)
        html = render_template(
            "docente/grupo_form.html",
            materias=materias,
            periodos=periodos,
            error=None,
            valores={},
        )
        send_html(handler, 200, html)
    elif method == "POST":
        body        = read_form_body(handler)
        nombre      = body.get("nombre", "").strip()
        periodo_id  = body.get("periodo_id", "").strip()
        materia_id  = body.get("materia_id", "").strip()
        cupo_str    = body.get("cupo_maximo", "").strip()
        cupo_maximo = int(cupo_str) if cupo_str and cupo_str.isdigit() else None
        horarios    = [{
            "dia_semana":  body.get("dia_semana", "").strip(),
            "hora_inicio": body.get("hora_inicio", "").strip(),
            "hora_fin":    body.get("hora_fin", "").strip(),
        }]
        try:
            grupo_business.crear(docente_id, periodo_id, materia_id, nombre, cupo_maximo, horarios)
            send_redirect(handler, "/docente/inicio")
        except (ValueError, LookupError) as e:
            materias = materia_business.listar(docente_id)
            periodos = periodo_business.listar(docente_id)
            html = render_template(
                "docente/grupo_form.html",
                materias=materias,
                periodos=periodos,
                error=str(e),
                valores=body,
            )
            send_html(handler, 400, html)
    else:
        send_error(handler, 405, "Método no permitido")


def _listar_inscripciones(handler, grupo_id: str):
    try:
        inscripciones = inscripcion_business.listar_por_grupo(grupo_id)
        grupo_nombre  = inscripciones[0]["grupo_nombre"] if inscripciones else "Grupo"
        html = render_template(
            "docente/grupo_inscripciones.html",
            grupo_id=grupo_id,
            grupo_nombre=grupo_nombre,
            inscripciones=inscripciones,
        )
        send_html(handler, 200, html)
    except Exception as e:
        send_error(handler, 500, f"Error al cargar inscripciones: {str(e)}")


def _accion_inscripcion(handler, method: str, inscripcion_id: str, accion: str):
    if method != "POST":
        send_error(handler, 405, "Método no permitido")
        return
    fn = _ACCIONES.get(accion)
    if not fn:
        send_error(handler, 404, "Acción no válida")
        return
    try:
        resultado = fn(inscripcion_id)
        grupo_id  = resultado.get("grupo_id", "")
        send_redirect(handler, f"/docente/grupos/{grupo_id}/inscripciones")
    except (ValueError, LookupError) as e:
        send_error(handler, 400, str(e))
    except Exception:
        send_error(handler, 500, "Error interno del servidor")
