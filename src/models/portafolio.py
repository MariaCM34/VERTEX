from datetime import datetime, date
from typing import List, Optional

from .activo import Activo
from .accion import Accion
from .posicion import Posicion
from .transaccion import Transaccion


class Portafolio:
    """Gestor principal del portafolio de inversión."""

    def __init__(self, capital_inicial: float, comision_broker: float = 0.001):
        if capital_inicial <= 0:
            raise ValueError(f"El capital inicial debe ser positivo: {capital_inicial}")

        if comision_broker < 0:
            raise ValueError(f"La comisión del broker no puede ser negativa: {comision_broker}")

        self.capital_inicial = capital_inicial
        self.capital_disponible = capital_inicial
        self.comision_broker = comision_broker
        self.posiciones: List[Posicion] = []
        self.transacciones: List[Transaccion] = []
        self.historial_valor: List[tuple[datetime, float]] = []

    def _buscar_posicion(self, activo: Activo) -> Optional[Posicion]:
        """Busca una posición existente para un activo."""
        for posicion in self.posiciones:
            if posicion.activo.simbolo == activo.simbolo:
                return posicion
        return None

    def validar_capital(self, monto: float) -> bool:
        """Verifica si hay capital disponible suficiente."""
        return self.capital_disponible >= monto

    def comprar_activo(
        self,
        activo: Activo,
        cantidad: int,
        precio: float,
        fecha: datetime | date
    ) -> bool:
        """
        Ejecuta una compra de activo.

        Valida capital disponible, precio (si es acción), actualiza posiciones y registra transacción.
        """
        if cantidad <= 0:
            raise ValueError(f"La cantidad debe ser positiva: {cantidad}")

        if precio <= 0:
            raise ValueError(f"El precio debe ser positivo: {precio}")

        if isinstance(activo, Accion):
            if not activo.validar_precio_en_rango(precio, fecha):
                raise ValueError(
                    f"El precio ${precio:.2f} está fuera del rango de mercado "
                    f"para {activo.simbolo} en {fecha}"
                )

        monto_bruto = cantidad * precio
        comision = monto_bruto * self.comision_broker
        monto_total = monto_bruto + comision

        if not self.validar_capital(monto_total):
            raise ValueError(
                f"Capital insuficiente. Requerido: ${monto_total:.2f}, "
                f"Disponible: ${self.capital_disponible:.2f}"
            )

        posicion = self._buscar_posicion(activo)
        if posicion:
            posicion.actualizar_compra(cantidad, precio)
        else:
            nueva_posicion = Posicion(activo, cantidad, precio)
            self.posiciones.append(nueva_posicion)

        transaccion = Transaccion(fecha, "compra", activo, cantidad, precio, comision)
        self.transacciones.append(transaccion)

        self.capital_disponible -= monto_total

        return True

    def vender_activo(
        self,
        activo: Activo,
        cantidad: int,
        precio: float,
        fecha: datetime | date
    ) -> bool:
        """
        Ejecuta una venta de activo.

        Valida existencia de posición, cantidad suficiente, precio (si es acción),
        actualiza posiciones y registra transacción.
        """
        if cantidad <= 0:
            raise ValueError(f"La cantidad debe ser positiva: {cantidad}")

        if precio <= 0:
            raise ValueError(f"El precio debe ser positivo: {precio}")

        posicion = self._buscar_posicion(activo)
        if not posicion:
            raise ValueError(f"No existe posición para {activo.simbolo}")

        if posicion.cantidad < cantidad:
            raise ValueError(
                f"Cantidad insuficiente para vender. "
                f"Disponible: {posicion.cantidad}, Solicitado: {cantidad}"
            )

        if isinstance(activo, Accion):
            if not activo.validar_precio_en_rango(precio, fecha):
                raise ValueError(
                    f"El precio ${precio:.2f} está fuera del rango de mercado "
                    f"para {activo.simbolo} en {fecha}"
                )

        monto_bruto = cantidad * precio
        comision = monto_bruto * self.comision_broker
        monto_neto = monto_bruto - comision

        posicion.actualizar_venta(cantidad)

        if posicion.cantidad == 0:
            self.posiciones.remove(posicion)

        transaccion = Transaccion(fecha, "venta", activo, cantidad, precio, comision)
        self.transacciones.append(transaccion)

        self.capital_disponible += monto_neto

        return True

    def agregar_dividendos(self, fecha_inicio: datetime | date, fecha_fin: datetime | date) -> None:
        """
        Calcula y agrega dividendos al capital disponible para el rango de fechas.

        Los dividendos NO se reinvierten automáticamente.
        """
        total_dividendos = 0.0

        for posicion in self.posiciones:
            if isinstance(posicion.activo, Accion):
                dividendos_por_accion = posicion.activo.obtener_dividendos(fecha_inicio, fecha_fin)
                total_dividendos += dividendos_por_accion * posicion.cantidad

        self.capital_disponible += total_dividendos

    def actualizar_valor_portafolio(self, fecha: datetime | date) -> None:
        """Calcula y registra el valor total del portafolio en una fecha."""
        if isinstance(fecha, date) and not isinstance(fecha, datetime):
            fecha = datetime.combine(fecha, datetime.min.time())

        valor_total = self.calcular_valor_total(fecha)
        self.historial_valor.append((fecha, valor_total))

    def calcular_valor_total(self, fecha: datetime | date) -> float:
        """Calcula el valor total del portafolio (capital disponible + valor de posiciones)."""
        valor_posiciones = sum(
            posicion.obtener_valor_actual(fecha)
            for posicion in self.posiciones
        )

        return self.capital_disponible + valor_posiciones

    def calcular_rentabilidad_neta(self) -> float:
        """
        Calcula la rentabilidad neta del portafolio.

        Requiere haber actualizado el valor del portafolio al menos una vez.
        """
        if not self.historial_valor:
            raise ValueError("No hay datos de valor histórico. Ejecute actualizar_valor_portafolio() primero.")

        valor_actual = self.historial_valor[-1][1]
        return (valor_actual - self.capital_inicial) / self.capital_inicial

    def calcular_valor_total_actual(self, api_quote) -> float:
        """
        Calcula el valor total del portafolio usando precios actuales de mercado.

        Para acciones usa QuoteAPI (precios en tiempo real).
        Para renta fija usa valoración calculada a fecha actual.

        Args:
            api_quote: Instancia de QuoteAPI para consultar precios actuales

        Returns:
            Valor total del portafolio (capital disponible + valor de posiciones actuales)

        Raises:
            ValueError: Si algún símbolo de acción no existe
            ConnectionError: Si hay error de conexión con la API
        """
        valor_posiciones = 0.0

        for posicion in self.posiciones:
            if isinstance(posicion.activo, Accion):
                # Acción: usar precio actual de mercado
                precio_actual = posicion.activo.obtener_precio_actual_mercado(api_quote)
                valor_posiciones += posicion.cantidad * precio_actual
            else:
                # Renta fija u otros: usar valoración calculada a fecha actual
                valor_posiciones += posicion.obtener_valor_actual(datetime.now())

        return self.capital_disponible + valor_posiciones

    def mostrar_resumen(self) -> str:
        """Genera un resumen del estado actual del portafolio."""
        lineas = []
        lineas.append("=" * 60)
        lineas.append("RESUMEN DEL PORTAFOLIO")
        lineas.append("=" * 60)
        lineas.append(f"Capital Inicial:    ${self.capital_inicial:,.2f}")
        lineas.append(f"Capital Disponible: ${self.capital_disponible:,.2f}")
        lineas.append(f"Comisión Broker:    {self.comision_broker * 100:.2f}%")
        lineas.append("")

        lineas.append(f"Posiciones Activas: {len(self.posiciones)}")
        if self.posiciones:
            lineas.append("-" * 60)
            for posicion in self.posiciones:
                valor_invertido = posicion.cantidad * posicion.costo_promedio
                lineas.append(
                    f"  {posicion.activo.simbolo:8} | "
                    f"Cant: {posicion.cantidad:6} | "
                    f"Costo Prom: ${posicion.costo_promedio:8.2f} | "
                    f"Invertido: ${valor_invertido:12,.2f}"
                )

        lineas.append("")
        lineas.append(f"Transacciones Realizadas: {len(self.transacciones)}")

        if self.historial_valor:
            valor_actual = self.historial_valor[-1][1]
            rentabilidad = self.calcular_rentabilidad_neta() * 100
            lineas.append("")
            lineas.append(f"Valor Total Actual: ${valor_actual:,.2f}")
            lineas.append(f"Rentabilidad Neta:  {rentabilidad:+.2f}%")

        lineas.append("=" * 60)

        return "\n".join(lineas)

    def __repr__(self) -> str:
        return (
            f"Portafolio(capital=${self.capital_inicial:,.2f}, "
            f"posiciones={len(self.posiciones)}, "
            f"transacciones={len(self.transacciones)})"
        )
