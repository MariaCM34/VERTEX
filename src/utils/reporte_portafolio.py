"""
Generador de reportes para el portafolio de inversión.

Proporciona funcionalidades para generar reportes formateados del estado del portafolio,
incluyendo resumen general, detalle por posición y comparativos histórico vs actual.
"""
from datetime import datetime
from typing import Optional
from src.models import Portafolio, Accion


class ReportePortafolio:
    """Generador de reportes formateados del portafolio."""

    @staticmethod
    def generar_reporte_completo(
        portafolio: Portafolio,
        fecha: Optional[datetime] = None
    ) -> str:
        """
        Genera un reporte completo del portafolio usando datos históricos.

        Args:
            portafolio: Instancia del portafolio
            fecha: Fecha para valoración histórica. Si es None, usa la última fecha del historial

        Returns:
            String con el reporte formateado
        """
        lineas = []
        lineas.append("=" * 80)
        lineas.append("REPORTE COMPLETO DEL PORTAFOLIO")
        lineas.append("=" * 80)

        # Resumen general
        lineas.append(ReportePortafolio._generar_resumen_general(portafolio, fecha))

        # Detalle de posiciones
        if portafolio.posiciones:
            lineas.append("\n" + ReportePortafolio.generar_detalle_posiciones(portafolio, fecha))

        # Historial de transacciones
        lineas.append(ReportePortafolio._generar_resumen_transacciones(portafolio))

        lineas.append("=" * 80)

        return "\n".join(lineas)

    @staticmethod
    def generar_detalle_posiciones(
        portafolio: Portafolio,
        fecha: Optional[datetime] = None
    ) -> str:
        """
        Genera tabla detallada de todas las posiciones del portafolio.

        Args:
            portafolio: Instancia del portafolio
            fecha: Fecha para valoración. Si es None, usa datetime.now()

        Returns:
            String con la tabla de posiciones formateada
        """
        if not portafolio.posiciones:
            return "\nNo hay posiciones activas en el portafolio."

        if fecha is None:
            fecha = datetime.now()

        lineas = []
        lineas.append("-" * 80)
        lineas.append("DETALLE DE POSICIONES")
        lineas.append("-" * 80)

        # Encabezado de tabla
        lineas.append(
            f"{'Símbolo':<10} {'Tipo':<12} {'Cantidad':>10} {'Costo Prom':>12} "
            f"{'Valor Actual':>14} {'G/P':>12} {'G/P %':>10}"
        )
        lineas.append("-" * 80)

        valor_total_posiciones = 0.0
        ganancia_total = 0.0

        for posicion in portafolio.posiciones:
            simbolo = posicion.activo.simbolo
            tipo_activo = posicion.activo.tipo
            cantidad = posicion.cantidad
            costo_promedio = posicion.costo_promedio

            # Calcular valor actual y ganancia/pérdida
            try:
                valor_actual = posicion.obtener_valor_actual(fecha)
                ganancia_perdida = posicion.obtener_ganancia_perdida(fecha)
                valor_costo = cantidad * costo_promedio
                ganancia_pct = (ganancia_perdida / valor_costo * 100) if valor_costo > 0 else 0.0

                valor_total_posiciones += valor_actual
                ganancia_total += ganancia_perdida

                # Formatear línea
                gp_signo = "+" if ganancia_perdida >= 0 else ""
                lineas.append(
                    f"{simbolo:<10} {tipo_activo:<12} {cantidad:>10} ${costo_promedio:>11.2f} "
                    f"${valor_actual:>13,.2f} {gp_signo}${ganancia_perdida:>10,.2f} "
                    f"{gp_signo}{ganancia_pct:>9.2f}%"
                )

            except ValueError as e:
                # Si no hay datos para la fecha, mostrar error
                lineas.append(
                    f"{simbolo:<10} {tipo_activo:<12} {cantidad:>10} ${costo_promedio:>11.2f} "
                    f"{'N/A':>14} {'N/A':>12} {'N/A':>10}"
                )

        lineas.append("-" * 80)

        # Totales
        gp_total_signo = "+" if ganancia_total >= 0 else ""
        lineas.append(
            f"{'TOTAL':<10} {'':<12} {'':<10} {'':<12} "
            f"${valor_total_posiciones:>13,.2f} {gp_total_signo}${ganancia_total:>10,.2f}"
        )
        lineas.append("-" * 80)

        return "\n".join(lineas)

    @staticmethod
    def generar_reporte_con_valoracion_actual(
        portafolio: Portafolio,
        api_quote
    ) -> str:
        """
        Genera reporte completo usando precios actuales de mercado (QuoteAPI).

        Args:
            portafolio: Instancia del portafolio
            api_quote: Instancia de QuoteAPI para consultar precios actuales

        Returns:
            String con el reporte formateado con valoración actual
        """
        lineas = []
        lineas.append("=" * 80)
        lineas.append("REPORTE DE PORTAFOLIO - VALORACIÓN ACTUAL DE MERCADO")
        lineas.append("=" * 80)
        lineas.append(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lineas.append("")

        # Resumen general
        lineas.append(ReportePortafolio._generar_resumen_general_actual(portafolio, api_quote))

        # Detalle de posiciones con valoración actual
        if portafolio.posiciones:
            lineas.append("\n" + ReportePortafolio._generar_detalle_posiciones_actual(portafolio, api_quote))

        lineas.append("=" * 80)

        return "\n".join(lineas)

    @staticmethod
    def generar_comparativo(
        portafolio: Portafolio,
        api_quote,
        fecha_historica: Optional[datetime] = None
    ) -> str:
        """
        Genera reporte comparativo entre valoración histórica y actual.

        Args:
            portafolio: Instancia del portafolio
            api_quote: Instancia de QuoteAPI
            fecha_historica: Fecha para comparación histórica. Si es None, usa última del historial

        Returns:
            String con el reporte comparativo
        """
        lineas = []
        lineas.append("=" * 80)
        lineas.append("REPORTE COMPARATIVO: HISTÓRICO VS ACTUAL")
        lineas.append("=" * 80)

        # Determinar fecha histórica
        if fecha_historica is None and portafolio.historial_valor:
            fecha_historica = portafolio.historial_valor[-1][0]
            valor_historico = portafolio.historial_valor[-1][1]
        elif fecha_historica:
            valor_historico = portafolio.calcular_valor_total(fecha_historica)
        else:
            valor_historico = portafolio.capital_inicial

        # Calcular valor actual
        valor_actual = portafolio.calcular_valor_total_actual(api_quote)

        # Comparación
        diferencia = valor_actual - valor_historico
        diferencia_pct = (diferencia / valor_historico * 100) if valor_historico > 0 else 0.0

        fecha_hist_str = fecha_historica.strftime('%Y-%m-%d') if fecha_historica else "N/A"

        lineas.append(f"\nFecha histórica: {fecha_hist_str}")
        lineas.append(f"Fecha actual:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lineas.append("")
        lineas.append("-" * 80)
        lineas.append(f"Valor histórico ({fecha_hist_str}):  ${valor_historico:>16,.2f}")
        lineas.append(f"Valor actual (mercado):              ${valor_actual:>16,.2f}")
        lineas.append("-" * 80)

        dif_signo = "+" if diferencia >= 0 else ""
        lineas.append(f"Diferencia:                          {dif_signo}${diferencia:>15,.2f} ({dif_signo}{diferencia_pct:.2f}%)")
        lineas.append("-" * 80)

        lineas.append("=" * 80)

        return "\n".join(lineas)

    @staticmethod
    def _generar_resumen_general(
        portafolio: Portafolio,
        fecha: Optional[datetime] = None
    ) -> str:
        """Genera el resumen general con datos históricos."""
        lineas = []
        lineas.append("\nRESUMEN GENERAL")
        lineas.append("-" * 80)
        lineas.append(f"Capital Inicial:          ${portafolio.capital_inicial:>16,.2f}")
        lineas.append(f"Capital Disponible:       ${portafolio.capital_disponible:>16,.2f}")
        lineas.append(f"Comisión Broker:          {portafolio.comision_broker * 100:>16.3f}%")
        lineas.append(f"Posiciones Activas:       {len(portafolio.posiciones):>16}")
        lineas.append(f"Transacciones Realizadas: {len(portafolio.transacciones):>16}")

        # Valor total histórico si existe
        if portafolio.historial_valor:
            valor_total = portafolio.historial_valor[-1][1]
            fecha_valor = portafolio.historial_valor[-1][0]
            rentabilidad = portafolio.calcular_rentabilidad_neta() * 100

            lineas.append("")
            lineas.append(f"Valor Total ({fecha_valor.strftime('%Y-%m-%d')}): ${valor_total:>16,.2f}")
            lineas.append(f"Rentabilidad Neta:        {rentabilidad:>16.2f}%")
        elif fecha:
            # Calcular valor para fecha específica
            try:
                valor_total = portafolio.calcular_valor_total(fecha)
                rentabilidad = ((valor_total - portafolio.capital_inicial) / portafolio.capital_inicial) * 100

                lineas.append("")
                lineas.append(f"Valor Total ({fecha.strftime('%Y-%m-%d')}):      ${valor_total:>16,.2f}")
                lineas.append(f"Rentabilidad:             {rentabilidad:>16.2f}%")
            except ValueError:
                pass

        lineas.append("-" * 80)

        return "\n".join(lineas)

    @staticmethod
    def _generar_resumen_general_actual(portafolio: Portafolio, api_quote) -> str:
        """Genera el resumen general con valoración actual."""
        lineas = []
        lineas.append("RESUMEN GENERAL")
        lineas.append("-" * 80)
        lineas.append(f"Capital Inicial:          ${portafolio.capital_inicial:>16,.2f}")
        lineas.append(f"Capital Disponible:       ${portafolio.capital_disponible:>16,.2f}")
        lineas.append(f"Comisión Broker:          {portafolio.comision_broker * 100:>16.3f}%")
        lineas.append(f"Posiciones Activas:       {len(portafolio.posiciones):>16}")

        # Valor actual con QuoteAPI
        valor_total_actual = portafolio.calcular_valor_total_actual(api_quote)
        rentabilidad_actual = ((valor_total_actual - portafolio.capital_inicial) / portafolio.capital_inicial) * 100
        ganancia_neta = valor_total_actual - portafolio.capital_inicial

        lineas.append("")
        lineas.append(f"Valor Total Actual:       ${valor_total_actual:>16,.2f}")
        ganancia_signo = "+" if ganancia_neta >= 0 else ""
        lineas.append(f"Ganancia/Pérdida:         {ganancia_signo}${ganancia_neta:>15,.2f}")
        lineas.append(f"Rentabilidad Actual:      {ganancia_signo}{rentabilidad_actual:>15.2f}%")
        lineas.append("-" * 80)

        return "\n".join(lineas)

    @staticmethod
    def _generar_detalle_posiciones_actual(portafolio: Portafolio, api_quote) -> str:
        """Genera tabla detallada con valoración actual de mercado."""
        if not portafolio.posiciones:
            return "\nNo hay posiciones activas en el portafolio."

        lineas = []
        lineas.append("-" * 80)
        lineas.append("DETALLE DE POSICIONES (PRECIOS ACTUALES DE MERCADO)")
        lineas.append("-" * 80)

        # Encabezado
        lineas.append(
            f"{'Símbolo':<10} {'Tipo':<12} {'Cantidad':>10} {'Costo Prom':>12} "
            f"{'Precio Actual':>14} {'Valor':>14} {'G/P':>12} {'G/P %':>10}"
        )
        lineas.append("-" * 80)

        valor_total_posiciones = 0.0
        ganancia_total = 0.0

        for posicion in portafolio.posiciones:
            simbolo = posicion.activo.simbolo
            tipo_activo = posicion.activo.tipo
            cantidad = posicion.cantidad
            costo_promedio = posicion.costo_promedio
            valor_costo = cantidad * costo_promedio

            try:
                # Obtener precio/valor actual según tipo de activo
                if isinstance(posicion.activo, Accion):
                    precio_actual = posicion.activo.obtener_precio_actual_mercado(api_quote)
                else:
                    # Renta fija u otros: calcular valor unitario actual
                    precio_actual = posicion.activo.obtener_valor_actual(datetime.now())

                valor_actual = cantidad * precio_actual
                ganancia_perdida = valor_actual - valor_costo
                ganancia_pct = (ganancia_perdida / valor_costo * 100) if valor_costo > 0 else 0.0

                valor_total_posiciones += valor_actual
                ganancia_total += ganancia_perdida

                # Formatear línea
                gp_signo = "+" if ganancia_perdida >= 0 else ""
                lineas.append(
                    f"{simbolo:<10} {tipo_activo:<12} {cantidad:>10} ${costo_promedio:>11.2f} "
                    f"${precio_actual:>13.2f} ${valor_actual:>13,.2f} "
                    f"{gp_signo}${ganancia_perdida:>10,.2f} {gp_signo}{ganancia_pct:>9.2f}%"
                )

            except (ValueError, ConnectionError) as e:
                lineas.append(
                    f"{simbolo:<10} {tipo_activo:<12} {cantidad:>10} ${costo_promedio:>11.2f} "
                    f"{'ERROR':>14} {'N/A':>14} {'N/A':>12} {'N/A':>10}"
                )

        lineas.append("-" * 80)

        # Totales
        gp_total_signo = "+" if ganancia_total >= 0 else ""
        lineas.append(
            f"{'TOTAL':<10} {'':<12} {'':<10} {'':<12} {'':<14} "
            f"${valor_total_posiciones:>13,.2f} {gp_total_signo}${ganancia_total:>10,.2f}"
        )
        lineas.append("-" * 80)

        return "\n".join(lineas)

    @staticmethod
    def _generar_resumen_transacciones(portafolio: Portafolio) -> str:
        """Genera resumen de transacciones realizadas."""
        lineas = []
        lineas.append("\nRESUMEN DE TRANSACCIONES")
        lineas.append("-" * 80)

        if not portafolio.transacciones:
            lineas.append("No hay transacciones registradas.")
            lineas.append("-" * 80)
            return "\n".join(lineas)

        # Contar transacciones por tipo
        compras = sum(1 for t in portafolio.transacciones if t.tipo == "compra")
        ventas = sum(1 for t in portafolio.transacciones if t.tipo == "venta")
        comision_total = sum(t.comision for t in portafolio.transacciones)

        lineas.append(f"Total de transacciones:   {len(portafolio.transacciones):>16}")
        lineas.append(f"  Compras:                {compras:>16}")
        lineas.append(f"  Ventas:                 {ventas:>16}")
        lineas.append(f"Comisiones pagadas:       ${comision_total:>16,.2f}")
        lineas.append("-" * 80)

        return "\n".join(lineas)
