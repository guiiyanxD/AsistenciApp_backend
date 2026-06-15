from abc import ABC, abstractmethod


class InscripcionState(ABC):

    @property
    @abstractmethod
    def valor(self) -> str: ...

    def inscribir(self, data, grupo_id: str, estudiante_id: str) -> dict:
        raise ValueError(f"No se puede inscribir desde el estado '{self.valor}'")

    def aprobar(self, data, inscripcion_id: str) -> dict:
        raise ValueError(f"No se puede aprobar una inscripción en estado '{self.valor}'")

    def reprobar(self, data, inscripcion_id: str) -> dict:
        raise ValueError(f"No se puede reprobar una inscripción en estado '{self.valor}'")

    def retirar(self, data, inscripcion_id: str) -> dict:
        raise ValueError(f"No se puede retirar una inscripción en estado '{self.valor}'")
