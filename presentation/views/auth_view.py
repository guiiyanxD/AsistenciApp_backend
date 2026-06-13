from business.auth_business import AuthBusiness
from utils.http_helpers import read_form_body, send_html, send_error, render_template

auth_business = AuthBusiness()


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
        if rol == "docente":
            if method == "GET":
                _mostrar_registro_docente(handler)
            elif method == "POST":
                _procesar_registro_docente(handler)
            else:
                send_error(handler, 405, "Método no permitido")
        elif rol == "estudiante":
            if method == "GET":
                _mostrar_registro_estudiante(handler)
            elif method == "POST":
                _procesar_registro_estudiante(handler)
            else:
                send_error(handler, 405, "Método no permitido")
        else:
            send_error(handler, 404, "Ruta no encontrada")


# ── Login ──────────────────────────────────────────────────────────────────────

def _mostrar_login(handler):
    html = render_template("login.html", error=None, rol="", email="")
    send_html(handler, 200, html)


def _procesar_login(handler):
    body = read_form_body(handler)
    rol = body.get("rol", "")
    email = body.get("email", "")
    password = body.get("password", "")

    try:
        if rol == "docente":
            resultado = auth_business.login_docente(email, password)
            token = resultado["token"]
            destino = "/docente/inicio"
        elif rol == "estudiante":
            resultado = auth_business.login_estudiante(email, password)
            token = resultado["token"]
            destino = "/estudiante/inicio"
        else:
            html = render_template("login.html", error="Selecciona un rol válido.", rol=rol, email=email)
            send_html(handler, 400, html)
            return

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


# ── Registro docente ───────────────────────────────────────────────────────────

def _mostrar_registro_docente(handler):
    html = render_template("registro_docente.html", error=None, datos={})
    send_html(handler, 200, html)


def _procesar_registro_docente(handler):
    body = read_form_body(handler)
    datos = {
        "nombre":    body.get("nombre", ""),
        "email":     body.get("email", ""),
        "profesion": body.get("profesion", ""),
    }

    try:
        resultado = auth_business.registrar_docente(
            datos["nombre"],
            datos["email"],
            body.get("password", ""),
            datos["profesion"],
        )
        token = resultado["token"]
        handler.send_response(302)
        handler.send_header("Location", "/docente/inicio")
        handler.send_header("Set-Cookie", f"session={token}; HttpOnly; Path=/; SameSite=Lax")
        handler.end_headers()

    except ValueError as e:
        html = render_template("registro_docente.html", error=str(e), datos=datos)
        send_html(handler, 400, html)
    except Exception:
        html = render_template("registro_docente.html", error="Error interno del servidor.", datos=datos)
        send_html(handler, 500, html)


# ── Registro estudiante ────────────────────────────────────────────────────────

def _mostrar_registro_estudiante(handler):
    html = render_template("registro_estudiante.html", error=None, datos={})
    send_html(handler, 200, html)


def _procesar_registro_estudiante(handler):
    body = read_form_body(handler)
    datos = {
        "nombre": body.get("nombre", ""),
        "email":  body.get("email", ""),
    }

    try:
        resultado = auth_business.registrar_estudiante(
            datos["nombre"],
            datos["email"],
            body.get("password", ""),
        )
        token = resultado["token"]
        handler.send_response(302)
        handler.send_header("Location", "/estudiante/inicio")
        handler.send_header("Set-Cookie", f"session={token}; HttpOnly; Path=/; SameSite=Lax")
        handler.end_headers()

    except ValueError as e:
        html = render_template("registro_estudiante.html", error=str(e), datos=datos)
        send_html(handler, 400, html)
    except Exception:
        html = render_template("registro_estudiante.html", error="Error interno del servidor.", datos=datos)
        send_html(handler, 500, html)
