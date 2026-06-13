from abc import ABC, abstractmethod


class RolStrategy(ABC):

    @abstractmethod
    def login(self, email: str, password: str) -> dict: ...

    @abstractmethod
    def registrar(self, body: dict) -> dict: ...

    @abstractmethod
    def get_dashboard_url(self) -> str: ...

    @abstractmethod
    def get_template_registro(self) -> str: ...

    @abstractmethod
    def extraer_datos_registro(self, body: dict) -> dict: ...
