from datetime import datetime, date

from .activo import Activo


class RentaFija(Activo):
    """Activo de renta fija con tasa de interés anual fija."""

    def __init__(
        self,
        nombre: str,
        simbolo: str,
        valor_nominal: float,
        tasa_anual: float,
        fecha_inicio: datetime | date,
        fecha_vencimiento: datetime | date
    ):
        super().__init__(nombre, simbolo, "renta_fija")

        if isinstance(fecha_inicio, date) and not isinstance(fecha_inicio, datetime):
            fecha_inicio = datetime.combine(fecha_inicio, datetime.min.time())
        if isinstance(fecha_vencimiento, date) and not isinstance(fecha_vencimiento, datetime):
            fecha_vencimiento = datetime.combine(fecha_vencimiento, datetime.max.time())

        if valor_nominal <= 0:
            raise ValueError(f"El valor nominal debe ser positivo: {valor_nominal}")

        if fecha_vencimiento <= fecha_inicio:
            raise ValueError(
                f"Fecha de vencimiento ({fecha_vencimiento.date()}) debe ser posterior "
                f"a fecha de inicio ({fecha_inicio.date()})"
            )

        self.valor_nominal = valor_nominal
        self.tasa_anual = tasa_anual
        self.fecha_inicio = fecha_inicio
        self.fecha_vencimiento = fecha_vencimiento

    def calcular_interes_diario(self) -> float:
        return (self.valor_nominal * self.tasa_anual) / 365

    def calcular_valor_en_fecha(self, fecha: datetime | date) -> float:
        """Calcula valor nominal + intereses acumulados hasta la fecha."""
        if isinstance(fecha, date) and not isinstance(fecha, datetime):
            fecha = datetime.combine(fecha, datetime.min.time())

        if fecha < self.fecha_inicio:
            raise ValueError(
                f"Fecha de consulta ({fecha.date()}) es anterior al inicio "
                f"del instrumento ({self.fecha_inicio.date()})"
            )

        fecha_calculo = min(fecha, self.fecha_vencimiento)
        dias_transcurridos = (fecha_calculo - self.fecha_inicio).days
        interes_acumulado = self.calcular_interes_diario() * dias_transcurridos

        return self.valor_nominal + interes_acumulado

    def obtener_valor_actual(self, fecha: datetime | date) -> float:
        return self.calcular_valor_en_fecha(fecha)

    def esta_vigente(self, fecha: datetime | date) -> bool:
        if isinstance(fecha, date) and not isinstance(fecha, datetime):
            fecha = datetime.combine(fecha, datetime.min.time())

        return self.fecha_inicio <= fecha <= self.fecha_vencimiento
