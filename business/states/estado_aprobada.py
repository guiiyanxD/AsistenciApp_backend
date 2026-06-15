from business.states.inscripcion_state import InscripcionState


class EstadoAprobada(InscripcionState):

    @property
    def valor(self) -> str:
        return "aprobada"

    def inscribir(self, data, grupo_id: str, estudiante_id: str) -> dict:
        raise ValueError("Ya aprobaste esta materia, no puedes reinscribirte")
