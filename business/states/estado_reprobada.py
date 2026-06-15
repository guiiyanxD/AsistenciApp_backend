from business.states.inscripcion_state import InscripcionState


class EstadoReprobada(InscripcionState):

    @property
    def valor(self) -> str:
        return "reprobada"

    def inscribir(self, data, grupo_id: str, estudiante_id: str) -> dict:
        return data.reactivar(grupo_id, estudiante_id)
