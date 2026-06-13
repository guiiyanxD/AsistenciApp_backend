from presentation.strategies.rol_strategy import RolStrategy
from presentation.strategies.docente_strategy import DocenteStrategy
from presentation.strategies.estudiante_strategy import EstudianteStrategy
from presentation.strategies.admin_strategy import AdminStrategy
from utils.http_helpers import read_form_body, send_html, send_error, render_template

_estrategias: dict[str, RolStrategy] = {
    "docente":    DocenteStrategy(),
    "estudiante": EstudianteStrategy(),
    "admin":      AdminStrategy(),
}


def handle_auth_web(handler, method: str, partes: list):
    accion = partes[0]  # "login", "logout" o "registro"

    if accion == "login":
        if method == "GET":
            _mostrar_login(handler)
        elif method == "POST":
            _procesar_login(handler)
        else:
            send_error(handler, 405, "Método no permitido")

    elif accion == "logout":
        _logout(handler)

    elif accion == "registro":
        rol = partes[1] if len(partes) >= 2 else ""
        estrategia = _estrategias.get(rol)
        if not estrategia:
            send_error(handler, 404, "Ruta no encontrada")
            return
        if method == "GET":
            _mostrar_registro(handler, estrategia)
        elif method == "POST":
            _procesar_registro(handler, estrategia)
        else:
            send_error(handler, 405, "Método no permitido")


# ── Login ──────────────────────────────────────────────────────────────────────

def _mostrar_login(handler):
    html = render_template("login.html", error=None, rol="", email="")
    send_html(handler, 200, html)


def _procesar_login(handler):
    body = read_form_body(handler)
    rol      = body.get("rol", "")
    email    = body.get("email", "")
    password = body.get("password", "")

    estrategia = _estrategias.get(rol)
    if not estrategia:
        html = render_template("login.html", error="Selecciona un rol válido.", rol=rol, email=email)
        send_html(handler, 400, html)
        return

    try:
        resultado = estrategia.login(email, password)
        token   = resultado["token"]
        destino = estrategia.get_dashboard_url()
        handler.send_response(302)
        handler.send_header("Location", destino)
        handler.send_header("Set-Cookie", f"session={token}; HttpOnly; Path=/; SameSite=Lax")
        handler.end_headers()

    except (ValueError, PermissionError) as e:
        html = render_template("login.html", error=str(e), rol=rol, email=email)
        send_html(handler, 400, html)
    except Exception:
        html = render_template("login.html", error="Error interno del servidor.", rol=rol, email=email)
        send_html(handler, 500, html)


def _logout(handler):
    handler.send_response(302)
    handler.send_header("Location", "/login")
    handler.send_header("Set-Cookie", "session=; HttpOnly; Path=/; Max-Age=0")
    handler.end_headers()


# ── Registro (genérico — delega en la Strategy activa) ────────────────────────

def _mostrar_registro(handler, estrategia: RolStrategy):
    html = render_template(estrategia.get_template_registro(), error=None, datos={})
    send_html(handler, 200, html)


def _procesar_registro(handler, estrategia: RolStrategy):
    body  = read_form_body(handler)
    datos = estrategia.extraer_datos_registro(body)

    try:
        resultado = estrategia.registrar(body)
        token   = resultado["token"]
        destino = estrategia.get_dashboard_url()
        handler.send_response(302)
        handler.send_header("Location", destino)
        handler.send_header("Set-Cookie", f"session={token}; HttpOnly; Path=/; SameSite=Lax")
        handler.end_headers()

    except ValueError as e:
        html = render_template(estrategia.get_template_registro(), error=str(e), datos=datos)
        send_html(handler, 400, html)
    except Exception:
        html = render_template(estrategia.get_template_registro(), error="Error interno del servidor.", datos=datos)
        send_html(handler, 500, html)
