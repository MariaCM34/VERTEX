from datetime import datetime, date

from .activo import Activo


class Transaccion:
    """Registro de una operación de compra o venta de un activo."""

    def __init__(
        self,
        fecha: datetime | date,
        tipo_operacion: str,
        activo: Activo,
        cantidad: int,
        precio_unitario: float,
        comision: float
    ):
        if isinstance(fecha, date) and not isinstance(fecha, datetime):
            fecha = datetime.combine(fecha, datetime.min.time())

        if tipo_operacion not in ["compra", "venta"]:
            raise ValueError(f"Tipo de operación inválido: {tipo_operacion}")

        if cantidad <= 0:
            raise ValueError(f"La cantidad debe ser positiva: {cantidad}")

        if precio_unitario <= 0:
            raise ValueError(f"El precio unitario debe ser positivo: {precio_unitario}")

        if comision < 0:
            raise ValueError(f"La comisión no puede ser negativa: {comision}")

        self.fecha = fecha
        self.tipo_operacion = tipo_operacion
        self.activo = activo
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.comision = comision
        self.monto_total = self.calcular_total()

    def calcular_total(self) -> float:
        """Calcula el monto total de la transacción incluyendo comisión."""
        monto_bruto = self.cantidad * self.precio_unitario

        if self.tipo_operacion == "compra":
            return monto_bruto + self.comision
        else:
            return monto_bruto - self.comision

    def __repr__(self) -> str:
        return (
            f"Transaccion({self.tipo_operacion.upper()}, "
            f"{self.activo.simbolo}, "
            f"{self.cantidad}x${self.precio_unitario:.2f}, "
            f"total=${self.monto_total:.2f})"
        )
