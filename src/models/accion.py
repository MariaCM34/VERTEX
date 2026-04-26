from datetime import datetime, date
from typing import List

from .activo import Activo
from .precio_diario import PrecioDiario
from .dividendo import Dividendo


class Accion(Activo):
    """Activo de renta variable con historial de precios y dividendos."""

    def __init__(self, nombre: str, simbolo: str):
        super().__init__(nombre, simbolo, "accion")
        self.historial_precios: List[PrecioDiario] = []
        self.historial_dividendos: List[Dividendo] = []

    def cargar_datos(
        self,
        api,
        fecha_inicio: datetime | date,
        fecha_fin: datetime | date
    ) -> None:
        """Carga datos históricos y dividendos desde HistoricalDataAPI."""
        precios = api.obtener_datos_historicos(self.simbolo, fecha_inicio, fecha_fin)
        for precio in precios:
            self.agregar_precio_diario(precio)

        dividendos = api.obtener_dividendos(self.simbolo, fecha_inicio, fecha_fin)
        for dividendo in dividendos:
            self.agregar_dividendo(dividendo)

    def agregar_precio_diario(self, precio_diario: PrecioDiario) -> None:
        self.historial_precios.append(precio_diario)
        self.historial_precios.sort(key=lambda p: p.fecha)

    def agregar_dividendo(self, dividendo: Dividendo) -> None:
        self.historial_dividendos.append(dividendo)
        self.historial_dividendos.sort(key=lambda d: d.fecha)

    def obtener_precio_cierre(self, fecha: datetime | date) -> float:
        if isinstance(fecha, date) and not isinstance(fecha, datetime):
            fecha = datetime.combine(fecha, datetime.min.time())

        for precio in self.historial_precios:
            if precio.fecha.date() == fecha.date():
                return precio.precio_cierre

        raise ValueError(f"No hay datos de precio para {self.simbolo} en {fecha.date()}")

    def obtener_rango_dia(self, fecha: datetime | date) -> PrecioDiario:
        if isinstance(fecha, date) and not isinstance(fecha, datetime):
            fecha = datetime.combine(fecha, datetime.min.time())

        for precio in self.historial_precios:
            if precio.fecha.date() == fecha.date():
                return precio

        raise ValueError(f"No hay datos de rango para {self.simbolo} en {fecha.date()}")

    def validar_precio_en_rango(self, precio: float, fecha: datetime | date) -> bool:
        """Valida que el precio esté dentro del rango min-max negociado ese día."""
        rango = self.obtener_rango_dia(fecha)
        return rango.validar_precio(precio)

    def obtener_dividendos(
        self,
        fecha_inicio: datetime | date,
        fecha_fin: datetime | date
    ) -> float:
        if isinstance(fecha_inicio, date) and not isinstance(fecha_inicio, datetime):
            fecha_inicio = datetime.combine(fecha_inicio, datetime.min.time())
        if isinstance(fecha_fin, date) and not isinstance(fecha_fin, datetime):
            fecha_fin = datetime.combine(fecha_fin, datetime.max.time())

        total = 0.0
        for dividendo in self.historial_dividendos:
            if fecha_inicio <= dividendo.fecha <= fecha_fin:
                total += dividendo.valor_por_accion

        return total

    def obtener_valor_actual(self, fecha: datetime | date) -> float:
        return self.obtener_precio_cierre(fecha)
