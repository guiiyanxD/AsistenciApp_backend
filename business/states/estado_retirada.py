from business.states.inscripcion_state import InscripcionState


class EstadoRetirada(InscripcionState):

    @property
    def valor(self) -> str:
        return "retirada"

    def inscribir(self, data, grupo_id: str, estudiante_id: str) -> dict:
        return data.reactivar(grupo_id, estudiante_id)
