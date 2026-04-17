from datetime import datetime, date


class PrecioDiario:
    """Información de precio de un activo en una fecha específica."""

    def __init__(
        self,
        fecha: datetime | date,
        precio_apertura: float,
        precio_cierre: float,
        precio_minimo: float,
        precio_maximo: float
    ):
        if isinstance(fecha, date) and not isinstance(fecha, datetime):
            fecha = datetime.combine(fecha, datetime.min.time())

        self.fecha = fecha
        self.precio_apertura = precio_apertura
        self.precio_cierre = precio_cierre
        self.precio_minimo = precio_minimo
        self.precio_maximo = precio_maximo

        self._validar_consistencia()

    def _validar_consistencia(self) -> None:
        if self.precio_minimo > self.precio_maximo:
            raise ValueError(
                f"Precio mínimo ({self.precio_minimo}) no puede ser mayor "
                f"que precio máximo ({self.precio_maximo})"
            )

        if not (self.precio_minimo <= self.precio_apertura <= self.precio_maximo):
            raise ValueError(
                f"Precio de apertura ({self.precio_apertura}) fuera del rango "
                f"[{self.precio_minimo}, {self.precio_maximo}]"
            )

        if not (self.precio_minimo <= self.precio_cierre <= self.precio_maximo):
            raise ValueError(
                f"Precio de cierre ({self.precio_cierre}) fuera del rango "
                f"[{self.precio_minimo}, {self.precio_maximo}]"
            )

    def validar_precio(self, precio: float) -> bool:
        return self.precio_minimo <= precio <= self.precio_maximo

    def __repr__(self) -> str:
        return (
            f"PrecioDiario(fecha={self.fecha.date()}, "
            f"apertura={self.precio_apertura:.2f}, "
            f"cierre={self.precio_cierre:.2f}, "
            f"min={self.precio_minimo:.2f}, "
            f"max={self.precio_maximo:.2f})"
        )
