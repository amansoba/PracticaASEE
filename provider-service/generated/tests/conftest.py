
import os
import sys
from pathlib import Path

import pytest
from dotenv import dotenv_values


# ============================================================
# CONFIGURACION DE RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"

sys.path.insert(0, str(SRC_DIR))


# ============================================================
# BASE DE DATOS EXCLUSIVA PARA TESTS
# ============================================================

ENV_TEST = BASE_DIR / ".env.test"

if not ENV_TEST.exists():
    raise RuntimeError(
        "No existe el archivo .env.test"
    )

configuracion = dotenv_values(ENV_TEST)

if configuracion.get("DB_NAME") != "subsonic_providers_test":
    raise RuntimeError(
        "Las pruebas deben usar exclusivamente "
        "subsonic_providers_test"
    )

for variable in (
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD"
):
    valor = configuracion.get(variable)

    if not valor:
        raise RuntimeError(
            f"Falta la variable {variable} en .env.test"
        )

    os.environ[variable] = valor

for variable in (
    "AUTH_SERVICE_URL",
    "EVENT_SERVICE_URL"
):
    valor = configuracion.get(variable)

    if valor:
        os.environ[variable] = valor


# ============================================================
# IMPORTACIONES DESPUES DE CONFIGURAR EL ENTORNO
# ============================================================

from fastapi.testclient import TestClient

from openapi_server.main import app
from openapi_server.database import engine
from openapi_server.db_models import Base


# ============================================================
# AISLAMIENTO ENTRE PRUEBAS
# ============================================================

@pytest.fixture(autouse=True)
def preparar_base_datos():

    if engine.url.database != "subsonic_providers_test":
        raise RuntimeError(
            "ERROR: Se ha intentado ejecutar un test "
            "fuera de la base de datos de pruebas"
        )

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


# ============================================================
# CLIENTE DE FASTAPI
# ============================================================

@pytest.fixture
def client():

    with TestClient(app) as cliente:
        yield cliente

    app.dependency_overrides.clear()
