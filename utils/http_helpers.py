import os
import mimetypes
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TEMPLATES_DIR = os.path.join(_BASE_DIR, "presentation", "templates")
_STATIC_DIR    = os.path.join(_BASE_DIR, "presentation", "static")

_jinja_env = Environment(loader=FileSystemLoader(_TEMPLATES_DIR), autoescape=True)


def render_template(plantilla: str, **contexto) -> str:
    template = _jinja_env.get_template(plantilla)
    return template.render(**contexto)


def send_html(handler: BaseHTTPRequestHandler, status: int, html: str):
    body = html.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def send_error(handler: BaseHTTPRequestHandler, status: int, message: str):
    html = (
        f"<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>Error {status}</title></head><body>"
        f"<h2>Error {status}</h2><p>{message}</p>"
        f"<a href='/login'>Volver al inicio</a></body></html>"
    )
    send_html(handler, status, html)


def send_redirect(handler: BaseHTTPRequestHandler, destino: str):
    handler.send_response(302)
    handler.send_header("Location", destino)
    handler.end_headers()


def read_form_body(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", 0))
    if length == 0:
        return {}
    raw = handler.rfile.read(length).decode("utf-8")
    parsed = parse_qs(raw)
    return {k: v[0] for k, v in parsed.items()}


def serve_static(handler: BaseHTTPRequestHandler, url_path: str):
    relative = url_path[len("/static"):].lstrip("/")
    file_path = os.path.normpath(os.path.join(_STATIC_DIR, relative))

    if not file_path.startswith(os.path.normpath(_STATIC_DIR)):
        send_error(handler, 403, "Acceso denegado")
        return

    if not os.path.isfile(file_path):
        send_error(handler, 404, "Archivo estático no encontrado")
        return

    mime, _ = mimetypes.guess_type(file_path)
    with open(file_path, "rb") as f:
        body = f.read()

    handler.send_response(200)
    handler.send_header("Content-Type", mime or "application/octet-stream")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)
