from business.auth_business import AuthBusiness
from presentation.strategies.rol_strategy import RolStrategy


class AdminStrategy(RolStrategy):

    def __init__(self):
        self._auth = AuthBusiness()

    def login(self, email: str, password: str) -> dict:
        return self._auth.login_admin(email, password)

    def registrar(self, body: dict) -> dict:
        return self._auth.registrar_admin(
            body.get("nombre", ""),
            body.get("email", ""),
            body.get("password", ""),
            body.get("cargo", ""),
            body.get("area", ""),
        )

    def get_dashboard_url(self) -> str:
        return "/admin/inicio"

    def get_template_registro(self) -> str:
        return "registro_admin.html"

    def extraer_datos_registro(self, body: dict) -> dict:
        return {
            "nombre": body.get("nombre", ""),
            "email":  body.get("email", ""),
            "cargo":  body.get("cargo", ""),
            "area":   body.get("area", ""),
        }
