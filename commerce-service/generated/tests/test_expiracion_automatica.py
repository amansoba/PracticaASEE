
import importlib
from threading import Event

from fastapi.testclient import TestClient


# Importamos el modulo completo para poder
# comprobar su ciclo de vida.
main = importlib.import_module("openapi_server.main")


# ============================================================
# TEST 1 - EJECUCION AUTOMATICA
# ============================================================

def test_expiracion_se_ejecuta_automaticamente(
    monkeypatch
):
    ejecutada = Event()

    # Simulamos la funcion de expiracion para
    # comprobar que el programador la ejecuta
    # sin modificar la base de datos.
    def expiracion_simulada():
        ejecutada.set()
        return 0

    monkeypatch.setattr(
        main,
        "expirar_pedidos_pendientes",
        expiracion_simulada
    )

    # Reducimos el intervalo exclusivamente
    # durante esta prueba.
    monkeypatch.setattr(
        main,
        "INTERVALO_REVISION_SEGUNDOS",
        0.05
    )

    # Arrancamos FastAPI y esperamos a que
    # ejecute la tarea automaticamente.
    with TestClient(main.app):
        assert ejecutada.wait(timeout=2)


# ============================================================
# TEST 2 - RECUPERACION TRAS UN ERROR
# ============================================================

def test_expiracion_continua_tras_un_error(
    monkeypatch
):
    recuperada = Event()
    intentos = [0]

    def expiracion_simulada():
        intentos[0] += 1

        # La primera ejecucion falla.
        if intentos[0] == 1:
            raise RuntimeError("Error simulado")

        # La segunda debe funcionar.
        recuperada.set()
        return 0

    monkeypatch.setattr(
        main,
        "expirar_pedidos_pendientes",
        expiracion_simulada
    )

    monkeypatch.setattr(
        main,
        "INTERVALO_REVISION_SEGUNDOS",
        0.05
    )

    with TestClient(main.app):
        assert recuperada.wait(timeout=2)

    assert intentos[0] >= 2
