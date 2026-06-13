import datetime
from data.repositories.clase_repository import ClaseRepository

TIPOS_VALIDOS = {"clase", "examen", "exposicion"}


class ClaseBusiness:

    def __init__(self):
        self.repo = ClaseRepository()

    def _obtener_y_verificar(self, clase_id: str, docente_id: str) -> dict:
        clase = self.repo.buscar_por_id(clase_id)
        if not clase:
            raise LookupError("Clase no encontrada")
        if str(clase["docente_id"]) != str(docente_id):
            raise PermissionError("No tienes acceso a esta clase")
        return clase

    def cambiar_tipo(self, clase_id: str, docente_id: str, tipo: str) -> dict:
        if tipo not in TIPOS_VALIDOS:
            raise ValueError(
                f"Tipo inválido. Valores permitidos: {', '.join(TIPOS_VALIDOS)}"
            )
        clase = self._obtener_y_verificar(clase_id, docente_id)
        if clase["cancelada"]:
            raise ValueError("No se puede etiquetar una clase cancelada. Restáurala primero.")
        actualizada = self.repo.actualizar_tipo(clase_id, tipo)
        if not actualizada:
            raise LookupError("Clase no encontrada")
        return actualizada

    def cancelar(self, clase_id: str, docente_id: str, observaciones: str) -> dict:
        if not observaciones or not observaciones.strip():
            raise ValueError("Las observaciones son obligatorias al cancelar una clase")
        clase = self._obtener_y_verificar(clase_id, docente_id)
        if clase["cancelada"]:
            raise ValueError("La clase ya está cancelada")
        cancelada = self.repo.cancelar(clase_id, observaciones.strip())
        if not cancelada:
            raise LookupError("Clase no encontrada")
        return cancelada

    def restaurar(self, clase_id: str, docente_id: str) -> dict:
        clase = self._obtener_y_verificar(clase_id, docente_id)
        if not clase["cancelada"]:
            raise ValueError("La clase no está cancelada")
        restaurada = self.repo.restaurar(clase_id)
        if not restaurada:
            raise LookupError("Clase no encontrada")
        return restaurada

    def crear_extraordinaria(self, docente_id: str, grupo_id: str,
                              fecha: str, hora_inicio: str,
                              hora_fin: str, tipo: str,
                              observaciones: str | None) -> dict:
        if tipo not in TIPOS_VALIDOS:
            raise ValueError(
                f"Tipo inválido. Valores permitidos: {', '.join(TIPOS_VALIDOS)}"
            )
        try:
            datetime.date.fromisoformat(fecha)
        except ValueError:
            raise ValueError("La fecha debe tener formato YYYY-MM-DD")
        try:
            hi = datetime.time.fromisoformat(hora_inicio)
            hf = datetime.time.fromisoformat(hora_fin)
        except ValueError:
            raise ValueError("Las horas deben tener formato HH:MM")
        if hf <= hi:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio")

        from data.repositories.grupo_repository import GrupoRepository
        grupo = GrupoRepository().buscar_por_id(grupo_id)
        if not grupo:
            raise LookupError("Grupo no encontrado")
        if str(grupo.get("docente_id")) != str(docente_id):
            raise PermissionError("No tienes acceso a este grupo")

        if self.repo.existe_clase_en_horario(grupo_id, fecha, hora_inicio):
            raise ValueError("Ya existe una clase para ese grupo en esa fecha y hora")

        return self.repo.crear_extraordinaria(
            grupo_id, fecha, hora_inicio, hora_fin, tipo, observaciones
        )

    def asistencias_clase(self, clase_id: str, docente_id: str) -> dict:
        clase = self._obtener_y_verificar(clase_id, docente_id)
        registros = self.repo.asistencias_con_ausentes(clase_id)

        presentes  = [r for r in registros if r.get("estado") == "presente"]
        pendientes = [r for r in registros if r.get("estado") == "pendiente"]
        ausentes   = [r for r in registros if r.get("asistencia_id") is None
                      or r.get("estado") == "ausente"]

        return {
            "clase": {
                "id": clase["id"],
                "fecha": str(clase["fecha"]),
                "hora_inicio": str(clase["hora_inicio"]),
                "hora_fin": str(clase["hora_fin"]),
                "tipo": clase["tipo"],
                "cancelada": clase["cancelada"],
            },
            "resumen": {
                "total_inscritos": len(registros),
                "presentes": len(presentes),
                "pendientes": len(pendientes),
                "ausentes": len(ausentes),
            },
            "registros": [self._formatear_registro(r) for r in registros],
        }

    def _formatear_registro(self, r: dict) -> dict:
        estado = r.get("estado") or "ausente"
        return {
            "estudiante_id":     str(r["estudiante_id"]),
            "estudiante_nombre": r["estudiante_nombre"],
            "estudiante_email":  r["estudiante_email"],
            "asistencia_id":     str(r["asistencia_id"]) if r.get("asistencia_id") else None,
            "estado":            estado,
            "fecha_marcado":     str(r["fecha_marcado"]) if r.get("fecha_marcado") else None,
            "latitud":           float(r["latitud"]) if r.get("latitud") else None,
            "longitud":          float(r["longitud"]) if r.get("longitud") else None,
        }
