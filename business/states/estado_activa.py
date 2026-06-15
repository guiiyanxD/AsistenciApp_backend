from business.states.inscripcion_state import InscripcionState


class EstadoActiva(InscripcionState):

    @property
    def valor(self) -> str:
        return "activa"

    def inscribir(self, data, grupo_id: str, estudiante_id: str) -> dict:
        raise ValueError("Ya estás inscrito en este grupo")

    def aprobar(self, data, inscripcion_id: str) -> dict:
        return data.actualizar_estado(inscripcion_id, "aprobada")

    def reprobar(self, data, inscripcion_id: str) -> dict:
        return data.actualizar_estado(inscripcion_id, "reprobada")

    def retirar(self, data, inscripcion_id: str) -> dict:
        return data.actualizar_estado(inscripcion_id, "retirada")
