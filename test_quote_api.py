"""
Prueba de integración con Finnhub mediante QuoteAPI
"""
from src.services import QuoteAPI


def test_precio_actual_valido():
    """Prueba obtención de precio actual con símbolo válido."""
    print("\n" + "=" * 60)
    print("PRUEBA 1: Precio actual de AAPL")
    print("=" * 60)

    try:
        api = QuoteAPI()
        simbolo = "AAPL"

        print(f"\nConsultando precio actual de {simbolo}...")
        precio = api.obtener_precio_actual(simbolo)

        print(f"[OK] Precio actual de {simbolo}: ${precio:.2f}")
        print(f"  Tipo de dato: {type(precio).__name__}")
        print(f"  Validación: {'PASS' if precio > 0 else 'FAIL'}")

        assert precio > 0, "El precio debe ser positivo"
        assert isinstance(precio, float), "El precio debe ser un float"

        print("\n[OK] Prueba exitosa")

    except ValueError as e:
        print(f"\n[ERROR] ValueError: {e}")
        raise

    except ConnectionError as e:
        print(f"\n[ERROR] ConnectionError: {e}")
        raise

    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        raise


def test_detalles_quote():
    """Prueba obtención de detalles completos del quote."""
    print("\n" + "=" * 60)
    print("PRUEBA 2: Detalles completos de MSFT")
    print("=" * 60)

    try:
        api = QuoteAPI()
        simbolo = "MSFT"

        print(f"\nConsultando detalles de {simbolo}...")
        detalles = api.obtener_detalles_quote(simbolo)

        print(f"\n[OK] Detalles de {simbolo}:")
        print(f"  Precio actual:    ${detalles['current']:.2f}")
        print(f"  Apertura:         ${detalles['open']:.2f}")
        print(f"  Máximo del día:   ${detalles['high']:.2f}")
        print(f"  Mínimo del día:   ${detalles['low']:.2f}")
        print(f"  Cierre anterior:  ${detalles['previous_close']:.2f}")

        # Validaciones
        assert detalles['current'] > 0, "Precio actual debe ser positivo"
        assert detalles['low'] <= detalles['high'], "Mínimo debe ser <= máximo"

        print("\n[OK] Prueba exitosa")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise


def test_simbolo_invalido():
    """Prueba manejo de error con símbolo inválido."""
    print("\n" + "=" * 60)
    print("PRUEBA 3: Símbolo inválido")
    print("=" * 60)

    try:
        api = QuoteAPI()
        simbolo_invalido = "INVALID_SYMBOL_XYZ123"

        print(f"\nIntentando consultar símbolo inválido: {simbolo_invalido}...")

        try:
            precio = api.obtener_precio_actual(simbolo_invalido)
            print(f"\n[FAIL] Debería haber lanzado ValueError pero retornó: {precio}")
            assert False, "Debería haber lanzado ValueError"

        except ValueError as e:
            print(f"[OK] ValueError capturado correctamente:")
            print(f"  Mensaje: {e}")
            print("\n[OK] Manejo de error correcto")

    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        raise


def test_multiples_simbolos():
    """Prueba consulta de múltiples símbolos populares."""
    print("\n" + "=" * 60)
    print("PRUEBA 4: Múltiples símbolos")
    print("=" * 60)

    simbolos = ["AAPL", "MSFT", "GOOGL", "TSLA"]

    try:
        api = QuoteAPI()

        print(f"\nConsultando {len(simbolos)} símbolos...")
        print("-" * 60)

        for simbolo in simbolos:
            try:
                precio = api.obtener_precio_actual(simbolo)
                print(f"  {simbolo:6} : ${precio:>8.2f}")
            except Exception as e:
                print(f"  {simbolo:6} : ERROR: {e}")

        print("-" * 60)
        print("\n[OK] Prueba completada")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise


def test_api_key_ausente():
    """Prueba que falla correctamente si no hay API key."""
    print("\n" + "=" * 60)
    print("PRUEBA 5: API key ausente")
    print("=" * 60)

    print("\nIntentando crear QuoteAPI con API key vacía...")

    try:
        # Pasar explícitamente una API key vacía (simula ausencia)
        api = QuoteAPI(api_key="")
        print(f"\n[FAIL] Debería haber lanzado ValueError")
        assert False, "Debería haber lanzado ValueError"

    except ValueError as e:
        print(f"[OK] ValueError capturado correctamente:")
        print(f"  Mensaje: {e}")
        print("\n[OK] Validación de API key correcta")


if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBAS DE QUOTEAPI CON FINNHUB")
    print("=" * 60)
    print("\nNOTA: Estas pruebas requieren:")
    print("  1. Conexión a internet")
    print("  2. API key de Finnhub en archivo .env")
    print("  3. Free tier permite 60 llamadas/minuto")

    try:
        # Pruebas principales
        test_precio_actual_valido()
        test_detalles_quote()
        test_multiples_simbolos()

        # Pruebas de validación
        test_simbolo_invalido()
        test_api_key_ausente()

        print("\n" + "=" * 60)
        print("[OK] TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print("[FAIL] PRUEBAS FALLIDAS")
        print("=" * 60)
        print(f"\nError: {e}")

        import traceback
        traceback.print_exc()
