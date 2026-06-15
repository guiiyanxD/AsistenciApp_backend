import datetime
from data.asistencia_data import AsistenciaData
from data.inscripcion_data import InscripcionData
from data.grupo_data import GrupoData


class AsistenciaBusiness:

    def __init__(self):
        self.repo = AsistenciaData()
        self.inscripcion_repo = InscripcionData()
        self.grupo_repo = GrupoData()

    def marcar(self, estudiante_id: str, grupo_id: str,
               latitud: float | None, longitud: float | None,
               precision_metros: float | None) -> dict:

        inscripcion = self.inscripcion_repo.buscar_inscripcion_activa(
            grupo_id, estudiante_id
        )
        if not inscripcion:
            raise PermissionError("No estás inscrito en este grupo")

        clase = self.repo.buscar_clase_activa(grupo_id)
        if not clase:
            raise ValueError(
                "No hay ninguna clase activa en este momento para este grupo"
            )

        if self.repo.existe_asistencia(clase["id"], inscripcion["id"]):
            raise ValueError("Ya marcaste tu asistencia en esta clase")

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
