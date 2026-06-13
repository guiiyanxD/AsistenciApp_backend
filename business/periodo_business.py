import datetime
from data.repositories.periodo_repository import PeriodoRepository

TIPOS_VALIDOS = {"mensual", "bimestral", "trimestral", "semestral", "anual", "personalizado"}


class PeriodoBusiness:

    def __init__(self):
        self.repo = PeriodoRepository()

    def crear(self, docente_id: str, nombre: str, tipo: str,
              fecha_inicio: str, fecha_fin: str) -> dict:
        self._validar_campos(nombre, tipo, fecha_inicio, fecha_fin)
        return self.repo.crear(docente_id, nombre.strip(), tipo, fecha_inicio, fecha_fin)

    def listar(self, docente_id: str) -> list[dict]:
        return self.repo.listar_por_docente(docente_id)

    def obtener(self, periodo_id: str, docente_id: str) -> dict:
        periodo = self.repo.buscar_por_id(periodo_id, docente_id)
        if not periodo:
            raise LookupError("Periodo académico no encontrado")
        return periodo

    def actualizar(self, periodo_id: str, docente_id: str, nombre: str, tipo: str,
                   fecha_inicio: str, fecha_fin: str, activo: bool) -> dict:
        self._validar_campos(nombre, tipo, fecha_inicio, fecha_fin)
        self.obtener(periodo_id, docente_id)
        actualizado = self.repo.actualizar(periodo_id, docente_id, nombre.strip(),
                                           tipo, fecha_inicio, fecha_fin, activo)
        if not actualizado:
            raise LookupError("Periodo académico no encontrado")
        return actualizado

    def eliminar(self, periodo_id: str, docente_id: str):
        self.obtener(periodo_id, docente_id)
        eliminado = self.repo.eliminar(periodo_id, docente_id)
        if not eliminado:
            raise LookupError("Periodo académico no encontrado")

    def _validar_campos(self, nombre: str, tipo: str, fecha_inicio: str, fecha_fin: str):
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del periodo es obligatorio")
        if tipo not in TIPOS_VALIDOS:
            raise ValueError(f"Tipo de periodo inválido. Valores permitidos: {', '.join(TIPOS_VALIDOS)}")
        try:
            fi = datetime.date.fromisoformat(fecha_inicio)
            ff = datetime.date.fromisoformat(fecha_fin)
        except ValueError:
            raise ValueError("Las fechas deben tener formato YYYY-MM-DD " + fecha_inicio + " " + fecha_fin)
        if ff <= fi:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")
