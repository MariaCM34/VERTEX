from datetime import datetime, date
from typing import List
import yfinance as yf

from ..models.precio_diario import PrecioDiario
from ..models.dividendo import Dividendo


class HistoricalDataAPI:
    """Servicio para obtener datos históricos y dividendos usando yfinance."""

    def __init__(self, fuente: str = "yfinance"):
        self.fuente = fuente

    def obtener_datos_historicos(
        self,
        simbolo: str,
        fecha_inicio: datetime | date,
        fecha_fin: datetime | date
    ) -> List[PrecioDiario]:
        """
        Obtiene datos históricos OHLC para un símbolo.

        Args:
            simbolo: Ticker del activo (ej: "AAPL", "MSFT")
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha de fin del rango

        Returns:
            Lista de PrecioDiario ordenada por fecha
        """
        if isinstance(fecha_inicio, datetime):
            fecha_inicio = fecha_inicio.date()
        if isinstance(fecha_fin, datetime):
            fecha_fin = fecha_fin.date()

        ticker = yf.Ticker(simbolo)
        hist = ticker.history(start=fecha_inicio, end=fecha_fin)

        precios = []
        for index, row in hist.iterrows():
            try:
                precio = PrecioDiario(
                    fecha=index.to_pydatetime(),
                    precio_apertura=float(row['Open']),
                    precio_cierre=float(row['Close']),
                    precio_minimo=float(row['Low']),
                    precio_maximo=float(row['High'])
                )
                precios.append(precio)
            except (KeyError, ValueError) as e:
                continue

        return precios

    def obtener_dividendos(
        self,
        simbolo: str,
        fecha_inicio: datetime | date,
        fecha_fin: datetime | date
    ) -> List[Dividendo]:
        """
        Obtiene dividendos pagados en un rango de fechas.

        Args:
            simbolo: Ticker del activo
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha de fin del rango

        Returns:
            Lista de Dividendo ordenada por fecha
        """
        if isinstance(fecha_inicio, datetime):
            fecha_inicio = fecha_inicio.date()
        if isinstance(fecha_fin, datetime):
            fecha_fin = fecha_fin.date()

        ticker = yf.Ticker(simbolo)
        divs_serie = ticker.dividends

        if divs_serie.empty:
            return []

        divs_filtrados = divs_serie[
            (divs_serie.index.date >= fecha_inicio) &
            (divs_serie.index.date <= fecha_fin)
        ]

        dividendos = []
        for index, valor in divs_filtrados.items():
            try:
                dividendo = Dividendo(
                    fecha=index.to_pydatetime(),
                    valor_por_accion=float(valor)
                )
                dividendos.append(dividendo)
            except (ValueError, TypeError) as e:
                continue

        return dividendos
