import bcrypt
from data.repositories.docente_repository import DocenteRepository
from data.repositories.estudiante_repository import EstudianteRepository
from utils.jwt_helper import generar_token


class AuthService:

    def __init__(self):
        self.docente_repo = DocenteRepository()
        self.estudiante_repo = EstudianteRepository()

    def registrar_docente(self, nombre: str, email: str, password: str, profesion: str) -> dict:
        if not nombre or not email or not password or not profesion:
            raise ValueError("Nombre, email, contraseña y profesión son obligatorios")
        if len(password) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if self.docente_repo.email_existe(email):
            raise ValueError("El email ya está registrado")
        if not profesion:
            profesion = "Ingeniero en sistemas"
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        docente = self.docente_repo.crear(nombre, email, password_hash, profesion)
        token = generar_token({"sub": str(docente["id"]), "rol": "docente"})
        return {"docente": docente, "token": token}

    def login_docente(self, email: str, password: str) -> dict:
        if not email or not password:
            raise ValueError("Email y contraseña son obligatorios")
        docente = self.docente_repo.buscar_por_email(email)
        if not docente:
            raise PermissionError("Credenciales incorrectas")
        if not bcrypt.checkpw(password.encode(), docente["password_hash"].encode()):
            raise PermissionError("Credenciales incorrectas")

        token = generar_token({"sub": str(docente["id"]), "rol": "docente"})
        docente.pop("password_hash", None)
        return {"docente": docente, "token": token}

    def registrar_estudiante(self, nombre: str, email: str, password: str) -> dict:
        if not nombre or not email or not password:
            raise ValueError("Nombre, email y contraseña son obligatorios")
        if len(password) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if self.estudiante_repo.email_existe(email):
            raise ValueError("El email ya está registrado")

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        estudiante = self.estudiante_repo.crear(nombre, email, password_hash)
        token = generar_token({"sub": str(estudiante["id"]), "rol": "estudiante"})
        return {"estudiante": estudiante, "token": token}

    def login_estudiante(self, email: str, password: str) -> dict:
        if not email or not password:
            raise ValueError("Email y contraseña son obligatorios")
        estudiante = self.estudiante_repo.buscar_por_email(email)
        if not estudiante:
            raise PermissionError("Credenciales incorrectas")
        if not bcrypt.checkpw(password.encode(), estudiante["password_hash"].encode()):
            raise PermissionError("Credenciales incorrectas")

        token = generar_token({"sub": str(estudiante["id"]), "rol": "estudiante"})
        estudiante.pop("password_hash", None)
        return {"estudiante": estudiante, "token": token}
