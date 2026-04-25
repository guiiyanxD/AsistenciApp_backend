import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from config.settings import Config
from presentation.router import enrutar


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):    self._despachar("GET")
    def do_POST(self):   self._despachar("POST")
    def do_PUT(self):    self._despachar("PUT")
    def do_DELETE(self): self._despachar("DELETE")
    def do_OPTIONS(self): self._despachar("OPTIONS")

    def _despachar(self, method: str):
        enrutar(self, method, self.path)

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")


def esperar_db(reintentos: int = 10, espera: int = 2):
    from config.database import get_connection
    for intento in range(1, reintentos + 1):
        try:
            conn = get_connection()
            conn.close()
            print("[DB] Conexión establecida correctamente")
            return
        except Exception as e:
            print(f"[DB] Intento {intento}/{reintentos} fallido: {e}")
            time.sleep(espera)
    print("[DB] No se pudo conectar a la base de datos. Abortando.")
    sys.exit(1)


if __name__ == "__main__":
    esperar_db()
    host = Config.SERVER_HOST
    port = Config.SERVER_PORT
    server = HTTPServer((host, port), RequestHandler)
    print(f"[SERVER] Servidor corriendo en http://{host}:{port}")
    print(f"[SERVER] Health check: http://{host}:{port}/api/health")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[SERVER] Servidor detenido")
        server.server_close()
