from data.repositories.materia_repository import MateriaRepository


class MateriaService:

    def __init__(self):
        self.repo = MateriaRepository()

    def crear(self, docente_id: str, nombre: str, codigo: str | None, descripcion: str | None) -> dict:
        if not nombre or not nombre.strip():
            raise ValueError("El nombre de la materia es obligatorio")
        if codigo and self.repo.codigo_existe(docente_id, codigo.strip()):
            raise ValueError(f"Ya existe una materia con el código '{codigo}'")
        return self.repo.crear(docente_id, nombre.strip(), codigo.strip() if codigo else None, descripcion)

    def listar(self, docente_id: str) -> list[dict]:
        return self.repo.listar_por_docente(docente_id)

    def obtener(self, materia_id: str, docente_id: str) -> dict:
        materia = self.repo.buscar_por_id(materia_id, docente_id)
        if not materia:
            raise LookupError("Materia no encontrada")
        return materia

    def actualizar(self, materia_id: str, docente_id: str, nombre: str,
                   codigo: str | None, descripcion: str | None) -> dict:
        if not nombre or not nombre.strip():
            raise ValueError("El nombre de la materia es obligatorio")
        self.obtener(materia_id, docente_id)
        actualizada = self.repo.actualizar(materia_id, docente_id, nombre.strip(),
                                           codigo.strip() if codigo else None, descripcion)
        if not actualizada:
            raise LookupError("Materia no encontrada")
        return actualizada

    def eliminar(self, materia_id: str, docente_id: str):
        self.obtener(materia_id, docente_id)
        eliminada = self.repo.eliminar(materia_id, docente_id)
        if not eliminada:
            raise ValueError("No se puede eliminar una materia asignada a un grupo activo")
