from business.auth_business import AuthBusiness
from presentation.strategies.rol_strategy import RolStrategy


class EstudianteStrategy(RolStrategy):

    def __init__(self):
        self._auth = AuthBusiness()

    def login(self, email: str, password: str) -> dict:
        return self._auth.login_estudiante(email, password)

    def registrar(self, body: dict) -> dict:
        return self._auth.registrar_estudiante(
            body.get("nombre", ""),
            body.get("email", ""),
            body.get("password", ""),
            body.get("codigo_estudiante", ""),
            body.get("carrera", ""),
            body.get("semestre", "1"),
        )

    def get_dashboard_url(self) -> str:
        return "/estudiante/inicio"

    def get_template_registro(self) -> str:
        return "registro_estudiante.html"

    def extraer_datos_registro(self, body: dict) -> dict:
        return {
            "nombre":           body.get("nombre", ""),
            "email":            body.get("email", ""),
            "codigo_estudiante": body.get("codigo_estudiante", ""),
            "carrera":          body.get("carrera", ""),
            "semestre":         body.get("semestre", "1"),
        }
