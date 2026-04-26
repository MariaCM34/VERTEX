"""
Visualizador de datos del portafolio usando matplotlib.

Proporciona métodos para generar gráficas de evolución, distribución y comparativos
del portafolio de inversión.
"""
from datetime import datetime
from typing import Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from src.models import Portafolio, Accion


class Visualizador:
    """Generador de visualizaciones del portafolio."""

    @staticmethod
    def graficar_evolucion_portafolio(
        portafolio: Portafolio,
        guardar_archivo: Optional[str] = None,
        mostrar: bool = True
    ) -> None:
        """
        Genera gráfica de línea mostrando la evolución del valor total del portafolio.

        Args:
            portafolio: Instancia del portafolio con historial poblado
            guardar_archivo: Ruta para guardar la figura (opcional)
            mostrar: Si True, muestra la gráfica interactivamente

        Raises:
            ValueError: Si el historial está vacío o tiene menos de 2 puntos
        """
        if not portafolio.historial_valor:
            raise ValueError(
                "El historial del portafolio está vacío. "
                "Ejecute portafolio.actualizar_valor_portafolio(fecha) primero."
            )

        if len(portafolio.historial_valor) < 2:
            raise ValueError(
                f"El historial tiene solo {len(portafolio.historial_valor)} punto(s). "
                "Se necesitan al menos 2 puntos para graficar evolución."
            )

        # Extraer fechas y valores
        fechas = [punto[0] for punto in portafolio.historial_valor]
        valores = [punto[1] for punto in portafolio.historial_valor]

        # Crear figura
        fig, ax = plt.subplots(figsize=(12, 6))

        # Graficar línea
        ax.plot(fechas, valores, marker='o', linewidth=2, markersize=6, label='Valor Total')

        # Línea horizontal del capital inicial
        ax.axhline(
            y=portafolio.capital_inicial,
            color='gray',
            linestyle='--',
            linewidth=1.5,
            label='Capital Inicial',
            alpha=0.7
        )

        # Configurar formato de fechas en eje X
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()  # Rotar fechas para mejor legibilidad

        # Etiquetas y título
        ax.set_xlabel('Fecha', fontsize=12, fontweight='bold')
        ax.set_ylabel('Valor Total ($)', fontsize=12, fontweight='bold')
        ax.set_title(
            'Evolución del Valor del Portafolio',
            fontsize=14,
            fontweight='bold',
            pad=20
        )

        # Grid para mejor lectura
        ax.grid(True, linestyle='--', alpha=0.3)

        # Leyenda
        ax.legend(loc='best', fontsize=10)

        # Formato de números en eje Y
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        # Ajustar layout
        plt.tight_layout()

        # Guardar si se especifica archivo
        if guardar_archivo:
            plt.savefig(guardar_archivo, dpi=300, bbox_inches='tight')
            print(f"[OK] Gráfica guardada en: {guardar_archivo}")

        # Mostrar si se solicita
        if mostrar:
            plt.show()
        else:
            plt.close()

    @staticmethod
    def graficar_distribucion_actual(
        portafolio: Portafolio,
        api_quote=None,
        guardar_archivo: Optional[str] = None,
        mostrar: bool = True
    ) -> None:
        """
        Genera gráfica de pie mostrando la distribución del portafolio por activo.

        Args:
            portafolio: Instancia del portafolio
            api_quote: Instancia de QuoteAPI para valoración actual (opcional)
            guardar_archivo: Ruta para guardar la figura (opcional)
            mostrar: Si True, muestra la gráfica interactivamente

        Raises:
            ValueError: Si no hay posiciones activas
        """
        # Filtrar posiciones con cantidad > 0
        posiciones_activas = [p for p in portafolio.posiciones if p.cantidad > 0]

        if not posiciones_activas:
            raise ValueError("No hay posiciones activas en el portafolio.")

        # Determinar fecha de valoración
        if api_quote:
            fecha_valoracion = None  # Usar valoración actual
        elif portafolio.historial_valor:
            fecha_valoracion = portafolio.historial_valor[-1][0]
        else:
            fecha_valoracion = datetime.now()

        # Calcular valores por posición
        simbolos = []
        valores = []

        for posicion in posiciones_activas:
            simbolo = posicion.activo.simbolo

            try:
                if api_quote and isinstance(posicion.activo, Accion):
                    # Valoración actual con QuoteAPI
                    precio_actual = posicion.activo.obtener_precio_actual_mercado(api_quote)
                    valor = posicion.cantidad * precio_actual
                elif fecha_valoracion:
                    # Valoración histórica
                    valor = posicion.obtener_valor_actual(fecha_valoracion)
                else:
                    # Fallback
                    valor = posicion.obtener_valor_actual(datetime.now())

                simbolos.append(simbolo)
                valores.append(valor)

            except (ValueError, ConnectionError) as e:
                print(f"[WARN] No se pudo valorar {simbolo}: {e}")
                continue

        if not valores:
            raise ValueError("No se pudo valorar ninguna posición del portafolio.")

        # Agregar capital disponible si es significativo
        if portafolio.capital_disponible > 0:
            simbolos.append('Efectivo')
            valores.append(portafolio.capital_disponible)

        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 8))

        # Crear pie chart
        wedges, texts, autotexts = ax.pie(
            valores,
            labels=simbolos,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 11}
        )

        # Mejorar formato de porcentajes
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)

        # Título
        titulo_valoracion = "Actual (Mercado)" if api_quote else "Última Valoración"
        ax.set_title(
            f'Distribución del Portafolio - {titulo_valoracion}',
            fontsize=14,
            fontweight='bold',
            pad=20
        )

        # Leyenda con valores
        leyenda_labels = [
            f"{simbolo}: ${valor:,.2f}"
            for simbolo, valor in zip(simbolos, valores)
        ]
        ax.legend(
            leyenda_labels,
            loc='center left',
            bbox_to_anchor=(1, 0.5),
            fontsize=9
        )

        # Ajustar layout
        plt.tight_layout()

        # Guardar si se especifica archivo
        if guardar_archivo:
            plt.savefig(guardar_archivo, dpi=300, bbox_inches='tight')
            print(f"[OK] Gráfica guardada en: {guardar_archivo}")

        # Mostrar si se solicita
        if mostrar:
            plt.show()
        else:
            plt.close()

    @staticmethod
    def graficar_comparativo_historico_vs_actual(
        portafolio: Portafolio,
        api_quote,
        guardar_archivo: Optional[str] = None,
        mostrar: bool = True
    ) -> None:
        """
        Genera gráfica de barras comparando valor histórico vs valor actual de mercado.

        Args:
            portafolio: Instancia del portafolio con historial poblado
            api_quote: Instancia de QuoteAPI para valoración actual
            guardar_archivo: Ruta para guardar la figura (opcional)
            mostrar: Si True, muestra la gráfica interactivamente

        Raises:
            ValueError: Si el historial está vacío
        """
        if not portafolio.historial_valor:
            raise ValueError(
                "El historial del portafolio está vacío. "
                "Ejecute portafolio.actualizar_valor_portafolio(fecha) primero."
            )

        # Obtener último valor histórico
        fecha_historica = portafolio.historial_valor[-1][0]
        valor_historico = portafolio.historial_valor[-1][1]

        # Calcular valor actual
        try:
            valor_actual = portafolio.calcular_valor_total_actual(api_quote)
        except (ValueError, ConnectionError) as e:
            raise ValueError(f"No se pudo obtener valor actual: {e}")

        # Calcular diferencia
        diferencia = valor_actual - valor_historico
        diferencia_pct = (diferencia / valor_historico * 100) if valor_historico > 0 else 0.0

        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 7))

        # Datos para barras
        categorias = ['Histórico\n' + fecha_historica.strftime('%Y-%m-%d'), 'Actual\n(Mercado)']
        valores_bar = [valor_historico, valor_actual]
        colores = ['steelblue', 'green' if diferencia >= 0 else 'red']

        # Crear barras
        barras = ax.bar(categorias, valores_bar, color=colores, alpha=0.7, width=0.6)

        # Agregar valores sobre las barras
        for i, (barra, valor) in enumerate(zip(barras, valores_bar)):
            altura = barra.get_height()
            ax.text(
                barra.get_x() + barra.get_width() / 2,
                altura,
                f'${valor:,.2f}',
                ha='center',
                va='bottom',
                fontsize=11,
                fontweight='bold'
            )

        # Línea horizontal del capital inicial
        ax.axhline(
            y=portafolio.capital_inicial,
            color='gray',
            linestyle='--',
            linewidth=1.5,
            label=f'Capital Inicial: ${portafolio.capital_inicial:,.2f}',
            alpha=0.7
        )

        # Etiquetas y título
        ax.set_ylabel('Valor Total ($)', fontsize=12, fontweight='bold')
        ax.set_title(
            'Comparativo: Valoración Histórica vs Actual',
            fontsize=14,
            fontweight='bold',
            pad=20
        )

        # Grid
        ax.grid(True, axis='y', linestyle='--', alpha=0.3)

        # Formato de números en eje Y
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        # Leyenda
        ax.legend(loc='upper left', fontsize=10)

        # Agregar texto con diferencia
        texto_diferencia = (
            f'Diferencia: {"+" if diferencia >= 0 else ""}'
            f'${diferencia:,.2f} ({diferencia_pct:+.2f}%)'
        )
        ax.text(
            0.5,
            0.95,
            texto_diferencia,
            transform=ax.transAxes,
            ha='center',
            va='top',
            fontsize=12,
            fontweight='bold',
            bbox=dict(
                boxstyle='round,pad=0.5',
                facecolor='lightyellow' if diferencia >= 0 else 'lightcoral',
                alpha=0.3
            )
        )

        # Ajustar layout
        plt.tight_layout()

        # Guardar si se especifica archivo
        if guardar_archivo:
            plt.savefig(guardar_archivo, dpi=300, bbox_inches='tight')
            print(f"[OK] Gráfica guardada en: {guardar_archivo}")

        # Mostrar si se solicita
        if mostrar:
            plt.show()
        else:
            plt.close()

    @staticmethod
    def graficar_rentabilidad_por_activo(
        portafolio: Portafolio,
        api_quote=None,
        guardar_archivo: Optional[str] = None,
        mostrar: bool = True
    ) -> None:
        """
        Genera gráfica de barras mostrando rentabilidad por activo.

        Args:
            portafolio: Instancia del portafolio
            api_quote: Instancia de QuoteAPI para valoración actual (opcional)
            guardar_archivo: Ruta para guardar la figura (opcional)
            mostrar: Si True, muestra la gráfica interactivamente

        Raises:
            ValueError: Si no hay posiciones activas
        """
        posiciones_activas = [p for p in portafolio.posiciones if p.cantidad > 0]

        if not posiciones_activas:
            raise ValueError("No hay posiciones activas en el portafolio.")

        # Determinar fecha de valoración
        if api_quote:
            fecha_valoracion = None
        elif portafolio.historial_valor:
            fecha_valoracion = portafolio.historial_valor[-1][0]
        else:
            fecha_valoracion = datetime.now()

        # Calcular rentabilidad por posición
        simbolos = []
        rentabilidades = []

        for posicion in posiciones_activas:
            simbolo = posicion.activo.simbolo
            valor_costo = posicion.cantidad * posicion.costo_promedio

            try:
                if api_quote and isinstance(posicion.activo, Accion):
                    precio_actual = posicion.activo.obtener_precio_actual_mercado(api_quote)
                    valor_actual = posicion.cantidad * precio_actual
                elif fecha_valoracion:
                    valor_actual = posicion.obtener_valor_actual(fecha_valoracion)
                else:
                    valor_actual = posicion.obtener_valor_actual(datetime.now())

                rentabilidad_pct = ((valor_actual - valor_costo) / valor_costo * 100) if valor_costo > 0 else 0.0

                simbolos.append(simbolo)
                rentabilidades.append(rentabilidad_pct)

            except (ValueError, ConnectionError) as e:
                print(f"[WARN] No se pudo calcular rentabilidad de {simbolo}: {e}")
                continue

        if not rentabilidades:
            raise ValueError("No se pudo calcular rentabilidad para ninguna posición.")

        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 6))

        # Colores según rentabilidad
        colores = ['green' if r >= 0 else 'red' for r in rentabilidades]

        # Crear barras horizontales
        barras = ax.barh(simbolos, rentabilidades, color=colores, alpha=0.7)

        # Agregar valores
        for i, (barra, valor) in enumerate(zip(barras, rentabilidades)):
            ancho = barra.get_width()
            ax.text(
                ancho,
                barra.get_y() + barra.get_height() / 2,
                f' {valor:+.2f}%',
                ha='left' if ancho >= 0 else 'right',
                va='center',
                fontsize=10,
                fontweight='bold'
            )

        # Línea vertical en 0
        ax.axvline(x=0, color='black', linewidth=1, linestyle='-')

        # Etiquetas y título
        ax.set_xlabel('Rentabilidad (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Activo', fontsize=12, fontweight='bold')

        titulo_valoracion = "Actual" if api_quote else "Última Valoración"
        ax.set_title(
            f'Rentabilidad por Activo - {titulo_valoracion}',
            fontsize=14,
            fontweight='bold',
            pad=20
        )

        # Grid
        ax.grid(True, axis='x', linestyle='--', alpha=0.3)

        # Ajustar layout
        plt.tight_layout()

        # Guardar si se especifica archivo
        if guardar_archivo:
            plt.savefig(guardar_archivo, dpi=300, bbox_inches='tight')
            print(f"[OK] Gráfica guardada en: {guardar_archivo}")

        # Mostrar si se solicita
        if mostrar:
            plt.show()
        else:
            plt.close()
