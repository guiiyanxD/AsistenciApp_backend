from business.states.inscripcion_state import InscripcionState


class EstadoActiva(InscripcionState):

    @property
    def valor(self) -> str:
        return "activa"

    def inscribir(self, repo, grupo_id: str, estudiante_id: str) -> dict:
        raise ValueError("Ya estás inscrito en este grupo")

    def aprobar(self, repo, inscripcion_id: str) -> dict:
        return repo.actualizar_estado(inscripcion_id, "aprobada")

    def reprobar(self, repo, inscripcion_id: str) -> dict:
        return repo.actualizar_estado(inscripcion_id, "reprobada")

    def retirar(self, repo, inscripcion_id: str) -> dict:
        return repo.actualizar_estado(inscripcion_id, "retirada")
