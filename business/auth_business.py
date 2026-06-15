import bcrypt
from data.docente_data import DocenteData
from data.estudiante_data import EstudianteData
from data.admin_data import AdminData
from utils.jwt_helper import generar_token


class AuthBusiness:

    def __init__(self):
        self.docente_data    = DocenteData()
        self.estudiante_data = EstudianteData()
        self.admin_data      = AdminData()

    # ── Docente ───────────────────────────────────────────────────────────────

    def registrar_docente(self, nombre: str, email: str, password: str,
                          profesion: str, titulo: str, departamento: str,
                          telefono: str) -> dict:
        if not all([nombre, email, password, profesion, titulo, departamento]):
            raise ValueError("Nombre, email, contraseña, profesión, título y departamento son obligatorios")
        if len(password) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if self.docente_data.email_existe(email):
            raise ValueError("El email ya está registrado")
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        docente = self.docente_data.crear(nombre, email, password_hash, profesion, titulo, departamento, telefono)
        token = generar_token({"sub": str(docente["id"]), "rol": "docente", "nombre": nombre})
        return {"docente": docente, "token": token}

    def login_docente(self, email: str, password: str) -> dict:
        if not email or not password:
            raise ValueError("Email y contraseña son obligatorios")
        docente = self.docente_data.buscar_por_email(email)
        if not docente:
            raise PermissionError("Credenciales incorrectas")
        if not bcrypt.checkpw(password.encode(), docente["password_hash"].encode()):
            raise PermissionError("Credenciales incorrectas")
        token = generar_token({"sub": str(docente["id"]), "rol": "docente", "nombre": docente["nombre"]})
        docente.pop("password_hash", None)
        return {"docente": docente, "token": token}

    # ── Estudiante ────────────────────────────────────────────────────────────

    def registrar_estudiante(self, nombre: str, email: str, password: str,
                             codigo_estudiante: str, carrera: str, semestre: int) -> dict:
        if not all([nombre, email, password, carrera]):
            raise ValueError("Nombre, email, contraseña y carrera son obligatorios")
        if len(password) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if self.estudiante_data.email_existe(email):
            raise ValueError("El email ya está registrado")
        try:
            semestre = int(semestre)
            if not (1 <= semestre <= 12):
                raise ValueError
        except (ValueError, TypeError):
            raise ValueError("El semestre debe ser un número entre 1 y 12")
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        estudiante = self.estudiante_data.crear(nombre, email, password_hash, codigo_estudiante, carrera, semestre)
        token = generar_token({"sub": str(estudiante["id"]), "rol": "estudiante", "nombre": nombre})
        return {"estudiante": estudiante, "token": token}

    def login_estudiante(self, email: str, password: str) -> dict:
        if not email or not password:
            raise ValueError("Email y contraseña son obligatorios")
        estudiante = self.estudiante_data.buscar_por_email(email)
        if not estudiante:
            raise PermissionError("Credenciales incorrectas")
        if not bcrypt.checkpw(password.encode(), estudiante["password_hash"].encode()):
            raise PermissionError("Credenciales incorrectas")
        token = generar_token({"sub": str(estudiante["id"]), "rol": "estudiante", "nombre": estudiante["nombre"]})
        estudiante.pop("password_hash", None)
        return {"estudiante": estudiante, "token": token}

    # ── Administrador ─────────────────────────────────────────────────────────

    def registrar_admin(self, nombre: str, email: str, password: str,
                        cargo: str, area: str) -> dict:
        if not all([nombre, email, password, cargo, area]):
            raise ValueError("Todos los campos son obligatorios")
        if len(password) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if self.admin_data.email_existe(email):
            raise ValueError("El email ya está registrado")
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        admin = self.admin_data.crear(nombre, email, password_hash, cargo, area)
        token = generar_token({"sub": str(admin["id"]), "rol": "admin", "nombre": nombre})
        return {"admin": admin, "token": token}

    def login_admin(self, email: str, password: str) -> dict:
        if not email or not password:
            raise ValueError("Email y contraseña son obligatorios")
        admin = self.admin_data.buscar_por_email(email)
        if not admin:
            raise PermissionError("Credenciales incorrectas")
        if not bcrypt.checkpw(password.encode(), admin["password_hash"].encode()):
            raise PermissionError("Credenciales incorrectas")
        token = generar_token({"sub": str(admin["id"]), "rol": "admin", "nombre": admin["nombre"]})
        admin.pop("password_hash", None)
        return {"admin": admin, "token": token}
