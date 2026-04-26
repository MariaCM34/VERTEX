"""
Servicio para obtener cotizaciones actuales usando Finnhub API.

Finnhub proporciona datos de mercado en tiempo real con un tier gratuito
de 60 llamadas por minuto, ideal para desarrollo y uso académico.
"""
import os
import requests
from typing import Optional
from dotenv import load_dotenv


class QuoteAPI:
    """Servicio para obtener precio actual de activos usando Finnhub."""

    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa QuoteAPI.

        Args:
            api_key: API key de Finnhub. Si no se provee, se lee desde .env
        """
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("FINNHUB_API_KEY")

        if not api_key:
            raise ValueError(
                "API key de Finnhub no encontrada. "
                "Configura FINNHUB_API_KEY en archivo .env o pásala al constructor."
            )

        self.api_key = api_key

    def obtener_precio_actual(self, simbolo: str) -> float:
        """
        Obtiene el precio actual (último precio negociado) de un activo.

        Args:
            simbolo: Ticker del activo (ej: "AAPL", "MSFT", "TSLA")

        Returns:
            Precio actual del activo

        Raises:
            ValueError: Si el símbolo es inválido o no se encuentra
            ConnectionError: Si hay error de conexión con la API
        """
        if not simbolo or not isinstance(simbolo, str):
            raise ValueError(f"Símbolo inválido: {simbolo}")

        simbolo = simbolo.strip().upper()

        url = f"{self.BASE_URL}/quote"
        params = {
            "symbol": simbolo,
            "token": self.api_key
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Finnhub retorna 'c' (current price) = 0 si el símbolo no existe
            if data.get('c') == 0 and data.get('pc') == 0:
                raise ValueError(
                    f"Símbolo '{simbolo}' no encontrado o sin datos disponibles"
                )

            precio_actual = data.get('c')

            if precio_actual is None:
                raise ValueError(
                    f"Respuesta inesperada de Finnhub para {simbolo}: {data}"
                )

            return float(precio_actual)

        except requests.exceptions.Timeout:
            raise ConnectionError(
                f"Timeout al consultar precio de {simbolo}. "
                "Verifica tu conexión a internet."
            )

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                raise ValueError(
                    "API key de Finnhub inválida o expirada. "
                    "Verifica tu FINNHUB_API_KEY en .env"
                )
            elif e.response.status_code == 429:
                raise ConnectionError(
                    "Límite de rate de Finnhub excedido. "
                    "Espera un minuto e intenta nuevamente."
                )
            else:
                raise ConnectionError(
                    f"Error HTTP {e.response.status_code} al consultar {simbolo}"
                )

        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"Error de conexión con Finnhub: {str(e)}"
            )

    def obtener_detalles_quote(self, simbolo: str) -> dict:
        """
        Obtiene detalles completos del quote (precio actual, alto, bajo, apertura).

        Args:
            simbolo: Ticker del activo

        Returns:
            Diccionario con:
                - current: precio actual
                - high: máximo del día
                - low: mínimo del día
                - open: precio de apertura
                - previous_close: cierre anterior
                - timestamp: marca de tiempo
        """
        simbolo = simbolo.strip().upper()

        url = f"{self.BASE_URL}/quote"
        params = {
            "symbol": simbolo,
            "token": self.api_key
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('c') == 0 and data.get('pc') == 0:
                raise ValueError(f"Símbolo '{simbolo}' no encontrado")

            return {
                'current': float(data.get('c', 0)),
                'high': float(data.get('h', 0)),
                'low': float(data.get('l', 0)),
                'open': float(data.get('o', 0)),
                'previous_close': float(data.get('pc', 0)),
                'timestamp': int(data.get('t', 0))
            }

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener detalles de {simbolo}: {str(e)}")
