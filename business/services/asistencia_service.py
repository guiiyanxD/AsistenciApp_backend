import datetime
from data.repositories.asistencia_repository import AsistenciaRepository
from data.repositories.inscripcion_repository import InscripcionRepository
from data.repositories.grupo_repository import GrupoRepository


class AsistenciaService:

    def __init__(self):
        self.repo = AsistenciaRepository()
        self.inscripcion_repo = InscripcionRepository()
        self.grupo_repo = GrupoRepository()

    def marcar(self, estudiante_id: str, grupo_id: str,
               latitud: float | None, longitud: float | None,
               precision_metros: float | None) -> dict:

        # 1. Verificar que el estudiante esté inscrito en el grupo
        inscripcion = self.inscripcion_repo.buscar_inscripcion_activa(
            grupo_id, estudiante_id
        )
        if not inscripcion:
            raise PermissionError("No estás inscrito en este grupo")

        # 2. Verificar que haya una clase activa en este momento
        clase = self.repo.buscar_clase_activa(grupo_id)
        if not clase:
            raise ValueError(
                "No hay ninguna clase activa en este momento para este grupo"
            )

        # 3. Verificar que no haya marcado ya en esta clase
        if self.repo.existe_asistencia(clase["id"], inscripcion["id"]):
            raise ValueError("Ya marcaste tu asistencia en esta clase")

        # 4. Registrar asistencia
        asistencia = self.repo.crear(
            clase["id"], inscripcion["id"],
            latitud, longitud, precision_metros
        )

        return {
            "asistencia": asistencia,
            "clase": {
                "id": clase["id"],
                "fecha": str(clase["fecha"]),
                "hora_inicio": str(clase["hora_inicio"]),
                "hora_fin": str(clase["hora_fin"]),
                "tipo": clase["tipo"],
            },
        }

    def listar_por_clase(self, clase_id: str, docente_id: str) -> list[dict]:
        # Verificar que la clase pertenece a un grupo del docente
        clase = self.repo.buscar_clase_por_id(clase_id)
        if not clase:
            raise LookupError("Clase no encontrada")

        grupo = self.grupo_repo.buscar_por_id(clase["grupo_id"])
        if not grupo or str(grupo.get("docente_id")) != str(docente_id):
            raise PermissionError("No tienes acceso a esta clase")

        return self.repo.listar_por_clase(clase_id)

    def resumen_por_grupo(self, grupo_id: str, docente_id: str) -> list[dict]:
        grupo = self.grupo_repo.buscar_por_id(grupo_id)
        if not grupo or str(grupo.get("docente_id")) != str(docente_id):
            raise PermissionError("No tienes acceso a este grupo")

        return self.repo.resumen_por_grupo(grupo_id)

    def historial_estudiante(self, grupo_id: str,
                              estudiante_id: str) -> list[dict]:
        inscripcion = self.inscripcion_repo.buscar_inscripcion_activa(
            grupo_id, estudiante_id
        )
        if not inscripcion:
            raise PermissionError("No estás inscrito en este grupo")

        return self.repo.listar_por_grupo_y_estudiante(grupo_id, estudiante_id)
