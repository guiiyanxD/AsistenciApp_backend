from business.states.inscripcion_state import InscripcionState


class EstadoReprobada(InscripcionState):

    @property
    def valor(self) -> str:
        return "reprobada"

    def inscribir(self, repo, grupo_id: str, estudiante_id: str) -> dict:
        return repo.reactivar(grupo_id, estudiante_id)
