"""
VERTEX - Simulador de Portafolio de Inversión
Punto de entrada principal de la aplicación
"""

import sys
from PySide6.QtWidgets import QApplication


def main():
    """
    Función principal que inicializa y ejecuta la aplicación.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("VERTEX")
    app.setOrganizationName("ITM")

    # TODO: Inicializar ventana principal cuando esté implementada
    # main_window = MainWindow()
    # main_window.show()

    print("VERTEX - Simulador de Portafolio de Inversión")
    print("Versión: 0.1.0 (Desarrollo)")
    print("Estructura base lista. Interfaz en construcción.")

    # sys.exit(app.exec())
    return 0


if __name__ == "__main__":
    sys.exit(main())
