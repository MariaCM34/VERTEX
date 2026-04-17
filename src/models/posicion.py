from datetime import datetime, date

from .activo import Activo


class Posicion:
    """Representa la tenencia actual de un activo dentro del portafolio."""

    def __init__(self, activo: Activo, cantidad: int, costo_promedio: float):
        if cantidad < 0:
            raise ValueError(f"La cantidad no puede ser negativa: {cantidad}")

        if costo_promedio < 0:
            raise ValueError(f"El costo promedio no puede ser negativo: {costo_promedio}")

        self.activo = activo
        self.cantidad = cantidad
        self.costo_promedio = costo_promedio

    def actualizar_compra(self, cantidad: int, precio: float) -> None:
        """Actualiza la posición con una nueva compra, recalculando el costo promedio ponderado."""
        if cantidad <= 0:
            raise ValueError(f"La cantidad de compra debe ser positiva: {cantidad}")

        if precio <= 0:
            raise ValueError(f"El precio debe ser positivo: {precio}")

        valor_actual = self.cantidad * self.costo_promedio
        valor_nuevo = cantidad * precio
        cantidad_total = self.cantidad + cantidad

        self.costo_promedio = (valor_actual + valor_nuevo) / cantidad_total
        self.cantidad = cantidad_total

    def actualizar_venta(self, cantidad: int) -> None:
        """Actualiza la posición con una venta, reduciendo la cantidad manteniendo el costo promedio."""
        if cantidad <= 0:
            raise ValueError(f"La cantidad de venta debe ser positiva: {cantidad}")

        if cantidad > self.cantidad:
            raise ValueError(
                f"No hay suficientes unidades para vender. "
                f"Disponible: {self.cantidad}, Solicitado: {cantidad}"
            )

        self.cantidad -= cantidad

    def obtener_valor_actual(self, fecha: datetime | date) -> float:
        """Calcula el valor de mercado actual de la posición."""
        precio_actual = self.activo.obtener_valor_actual(fecha)
        return self.cantidad * precio_actual

    def obtener_ganancia_perdida(self, fecha: datetime | date) -> float:
        """Calcula la ganancia o pérdida no realizada de la posición."""
        valor_actual = self.obtener_valor_actual(fecha)
        valor_costo = self.cantidad * self.costo_promedio
        return valor_actual - valor_costo

    def __repr__(self) -> str:
        return (
            f"Posicion({self.activo.simbolo}, "
            f"cantidad={self.cantidad}, "
            f"costo_promedio=${self.costo_promedio:.2f})"
        )
