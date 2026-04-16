<<<<<<< HEAD
# VERTEX - Simulador de Portafolio de Inversión

## Descripción

Aplicación de escritorio desarrollada en Python para simular y gestionar un portafolio de inversión. Permite registrar transacciones de compra y venta de activos financieros, calcular rentabilidad y visualizar resultados mediante gráficas modernas e interactivas.

## Características

- Registro y gestión de activos financieros (acciones, ETFs, criptomonedas)
- Simulación de transacciones de compra y venta
- Cálculo preciso de rentabilidad y métricas de rendimiento
- Dashboard visual con gráficas interactivas
- Interfaz gráfica moderna desarrollada con PySide6
- Integración con APIs financieras para datos en tiempo real

## Stack Tecnológico

- **Python 3.11+**
- **PySide6**: Interfaz gráfica de usuario
- **Matplotlib**: Visualización de datos y gráficas
- **Pandas**: Manipulación y análisis de datos
- **yfinance**: Datos financieros en tiempo real
- **requests**: Peticiones HTTP a APIs

## Instalación

### Prerrequisitos

- Python 3.11 o superior
- pip (gestor de paquetes de Python)

### Pasos

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd VERTEX
```

2. Crear entorno virtual:
```bash
python -m venv .venv
```

3. Activar entorno virtual:
- Windows:
  ```bash
  .venv\Scripts\activate
  ```
- Linux/Mac:
  ```bash
  source .venv/bin/activate
  ```

4. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

## Estructura del Proyecto

```
VERTEX/
├── src/                  # Código fuente
│   ├── models/          # Modelos de dominio (OOP)
│   ├── services/        # Lógica de negocio
│   ├── ui/              # Interfaz gráfica (PySide6)
│   └── utils/           # Utilidades y helpers
├── main.py              # Punto de entrada
├── requirements.txt     # Dependencias
└── README.md
```

## Desarrollo

### Arquitectura

El proyecto sigue principios de **Programación Orientada a Objetos** con separación clara de responsabilidades:

- **Models**: Clases de dominio (Activo, Transaccion, Portafolio)
- **Services**: Lógica de negocio y cálculos
- **UI**: Componentes de interfaz gráfica
- **Utils**: Funciones auxiliares y utilidades

### Fases de Desarrollo

#### Fase 1 (Actual)
- ✅ Estructura del proyecto
- 🔄 Modelado orientado a objetos
- 🔄 Implementación de clases base
- 🔄 Dashboard visual
- 🔄 Documentación base

#### Fase 2 (Planificada)
- Importación de datos desde CSV/Excel
- Análisis avanzados
- Mejoras visuales

## Autor

Proyecto Universitario - ITM
Estructura de Datos 2026-1

## Licencia

Proyecto académico - Uso educativo
=======
# VERTEX
Proyecto de simulación de portafolio de inversión con enfoque en análisis, visualización y experiencia de usuario
>>>>>>> 67e2e927fbd1ef5352be833815fef5e7c27f863b
