from abc import ABC, abstractmethod
from datetime import datetime, date


class Activo(ABC):
    """Clase base abstracta para activos financieros."""

    def __init__(self, nombre: str, simbolo: str, tipo: str):
        self.nombre = nombre
        self.simbolo = simbolo
        self.tipo = tipo

    def get_nombre(self) -> str:
        return self.nombre

    def get_simbolo(self) -> str:
        return self.simbolo

    def get_tipo(self) -> str:
        return self.tipo

    @abstractmethod
    def obtener_valor_actual(self, fecha: datetime | date) -> float:
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(simbolo={self.simbolo}, nombre={self.nombre})"
