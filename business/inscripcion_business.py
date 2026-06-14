import datetime
from data.repositories.inscripcion_repository import InscripcionRepository
from business.states.inscripcion_state import InscripcionState
from business.states.estado_activa import EstadoActiva
from business.states.estado_aprobada import EstadoAprobada
from business.states.estado_reprobada import EstadoReprobada
from business.states.estado_retirada import EstadoRetirada

_ESTADOS: dict[str, InscripcionState] = {
    "activa":    EstadoActiva(),
    "aprobada":  EstadoAprobada(),
    "reprobada": EstadoReprobada(),
    "retirada":  EstadoRetirada(),
}


class InscripcionBusiness:

    def __init__(self):
        self.repo = InscripcionRepository()

    def _resolver_estado(self, valor: str) -> InscripcionState:
        estado = _ESTADOS.get(valor)
        if not estado:
            raise ValueError(f"Estado de inscripción desconocido: '{valor}'")
        return estado

    def unirse_por_codigo(self, codigo: str, estudiante_id: str) -> dict:
        if not codigo or not codigo.strip():
            raise ValueError("El código de invitación es obligatorio")

        grupo = self.repo.buscar_grupo_por_codigo(codigo.strip().upper())
        if not grupo:
            raise LookupError("Código de invitación inválido o inexistente")

        if not grupo["activo"]:
            raise ValueError("Este grupo ya no está activo")

        if not grupo["periodo_activo"]:
            raise ValueError("El periodo académico de este grupo no está activo")

        fecha_fin = grupo["fecha_fin"]
        if isinstance(fecha_fin, str):
            fecha_fin = datetime.date.fromisoformat(fecha_fin)
        if fecha_fin < datetime.date.today():
            raise ValueError("El periodo académico de este grupo ya finalizó")

        if grupo["cupo_maximo"] is not None:
            inscritos = self.repo.contar_inscritos(grupo["id"])
            if inscritos >= grupo["cupo_maximo"]:
                raise ValueError("El grupo ha alcanzado su cupo máximo")

        inscripcion_previa = self.repo.buscar_por_grupo_y_estudiante(grupo["id"], estudiante_id)
        if inscripcion_previa:
            estado = self._resolver_estado(inscripcion_previa["estado"])
            inscripcion = estado.inscribir(self.repo, grupo["id"], estudiante_id)
        else:
            inscripcion = self.repo.crear(grupo["id"], estudiante_id)

        return {
            "inscripcion": inscripcion,
            "grupo": {
                "id":             grupo["id"],
                "nombre":         grupo["nombre"],
                "materia_nombre": grupo["materia_nombre"],
                "periodo_nombre": grupo["periodo_nombre"],
                "fecha_inicio":   str(grupo["fecha_inicio"]),
                "fecha_fin":      str(grupo["fecha_fin"]),
            },
        }

    def aprobar(self, inscripcion_id: str) -> dict:
        inscripcion = self.repo.buscar_por_id(inscripcion_id)
        if not inscripcion:
            raise LookupError("Inscripción no encontrada")
        estado = self._resolver_estado(inscripcion["estado"])
        return estado.aprobar(self.repo, inscripcion_id)

    def reprobar(self, inscripcion_id: str) -> dict:
        inscripcion = self.repo.buscar_por_id(inscripcion_id)
        if not inscripcion:
            raise LookupError("Inscripción no encontrada")
        estado = self._resolver_estado(inscripcion["estado"])
        return estado.reprobar(self.repo, inscripcion_id)

    def retirar(self, inscripcion_id: str) -> dict:
        inscripcion = self.repo.buscar_por_id(inscripcion_id)
        if not inscripcion:
            raise LookupError("Inscripción no encontrada")
        estado = self._resolver_estado(inscripcion["estado"])
        return estado.retirar(self.repo, inscripcion_id)

    def listar_por_grupo(self, grupo_id: str) -> list[dict]:
        return self.repo.listar_por_grupo(grupo_id)

    def listar_grupos_estudiante(self, estudiante_id: str) -> list[dict]:
        return self.repo.listar_por_estudiante(estudiante_id)
