from datetime import datetime, date


class Dividendo:
    """Registro de dividendo pagado en una fecha."""

    def __init__(self, fecha: datetime | date, valor_por_accion: float):
        if isinstance(fecha, date) and not isinstance(fecha, datetime):
            fecha = datetime.combine(fecha, datetime.min.time())

        if valor_por_accion < 0:
            raise ValueError(f"El valor del dividendo no puede ser negativo: {valor_por_accion}")

        self.fecha = fecha
        self.valor_por_accion = valor_por_accion

    def __repr__(self) -> str:
        return f"Dividendo(fecha={self.fecha.date()}, valor={self.valor_por_accion:.4f})"
