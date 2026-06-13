from business.auth_business import AuthBusiness
from presentation.strategies.rol_strategy import RolStrategy


class DocenteStrategy(RolStrategy):

    def __init__(self):
        self._auth = AuthBusiness()

    def login(self, email: str, password: str) -> dict:
        return self._auth.login_docente(email, password)

    def registrar(self, body: dict) -> dict:
        return self._auth.registrar_docente(
            body.get("nombre", ""),
            body.get("email", ""),
            body.get("password", ""),
            body.get("profesion", ""),
            body.get("titulo", ""),
            body.get("departamento", ""),
            body.get("telefono", ""),
        )

    def get_dashboard_url(self) -> str:
        return "/docente/inicio"

    def get_template_registro(self) -> str:
        return "registro_docente.html"

    def extraer_datos_registro(self, body: dict) -> dict:
        return {
            "nombre":       body.get("nombre", ""),
            "email":        body.get("email", ""),
            "profesion":    body.get("profesion", ""),
            "titulo":       body.get("titulo", ""),
            "departamento": body.get("departamento", ""),
            "telefono":     body.get("telefono", ""),
        }
