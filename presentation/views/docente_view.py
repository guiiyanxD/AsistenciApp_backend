from business.materia_business import MateriaBusiness
from business.periodo_business import PeriodoBusiness
from business.grupo_business import GrupoBusiness
from business.inscripcion_business import InscripcionBusiness
from presentation.middlewares.auth_middleware import solo_docente_web
from utils.http_helpers import send_html, send_error, send_redirect, render_template, read_form_body


class DocenteView:

    def __init__(self):
        self._materia_business     = MateriaBusiness()
        self._periodo_business     = PeriodoBusiness()
        self._grupo_business       = GrupoBusiness()
        self._inscripcion_business = InscripcionBusiness()
        self._ACCIONES = {
            "aprobar":  self._inscripcion_business.aprobar,
            "reprobar": self._inscripcion_business.reprobar,
            "retirar":  self._inscripcion_business.retirar,
        }

    def handle_docente_web(self, handler, method: str, partes: list):
        payload = solo_docente_web(handler)
        if not payload:
            return

        seccion = partes[1] if len(partes) >= 2 else "inicio"

        if seccion == "inicio" and method == "GET":
            self._inicio(handler, payload)

        elif seccion == "materias" and len(partes) >= 3 and partes[2] == "nueva":
            self._form_materia(handler, method, payload)

        elif seccion == "periodos" and len(partes) >= 3 and partes[2] == "nuevo":
            self._form_periodo(handler, method, payload)

        elif seccion == "grupos" and len(partes) >= 3 and partes[2] == "nuevo":
            self._form_grupo(handler, method, payload)

        elif seccion == "grupos" and len(partes) >= 4 and partes[3] == "inscripciones":
            self._listar_inscripciones(handler, partes[2])

        elif seccion == "inscripciones" and len(partes) >= 4:
            self._accion_inscripcion(handler, method, partes[2], partes[3])

        else:
            send_error(handler, 404, "Página no encontrada")

    # ── Panel principal ────────────────────────────────────────────────────────

    def _inicio(self, handler, payload: dict):
        docente_id = payload["sub"]
        nombre     = payload.get("nombre", "Docente")
        try:
            materias = self._materia_business.listar(docente_id)
            periodos = self._periodo_business.listar(docente_id)
            grupos   = self._grupo_business.listar(docente_id)
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

    # ── Materias ───────────────────────────────────────────────────────────────

    def _form_materia(self, handler, method: str, payload: dict):
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
                self._materia_business.crear(docente_id, nombre, codigo, descripcion)
                send_redirect(handler, "/docente/inicio")
            except (ValueError, LookupError) as e:
                html = render_template("docente/materia_form.html", error=str(e), valores=body)
                send_html(handler, 400, html)
        else:
            send_error(handler, 405, "Método no permitido")

    # ── Períodos ───────────────────────────────────────────────────────────────

    def _form_periodo(self, handler, method: str, payload: dict):
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
                self._periodo_business.crear(docente_id, nombre, tipo, fecha_inicio, fecha_fin)
                send_redirect(handler, "/docente/inicio")
            except (ValueError, LookupError) as e:
                html = render_template("docente/periodo_form.html", error=str(e), valores=body)
                send_html(handler, 400, html)
        else:
            send_error(handler, 405, "Método no permitido")

    # ── Grupos ─────────────────────────────────────────────────────────────────

    def _form_grupo(self, handler, method: str, payload: dict):
        docente_id = payload["sub"]
        if method == "GET":
            materias = self._materia_business.listar(docente_id)
            periodos = self._periodo_business.listar(docente_id)
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
                self._grupo_business.crear(docente_id, periodo_id, materia_id, nombre, cupo_maximo, horarios)
                send_redirect(handler, "/docente/inicio")
            except (ValueError, LookupError) as e:
                materias = self._materia_business.listar(docente_id)
                periodos = self._periodo_business.listar(docente_id)
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

    # ── Inscripciones ──────────────────────────────────────────────────────────

    def _listar_inscripciones(self, handler, grupo_id: str):
        try:
            inscripciones = self._inscripcion_business.listar_por_grupo(grupo_id)
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

    def _accion_inscripcion(self, handler, method: str, inscripcion_id: str, accion: str):
        if method != "POST":
            send_error(handler, 405, "Método no permitido")
            return
        fn = self._ACCIONES.get(accion)
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


docente_view = DocenteView()
