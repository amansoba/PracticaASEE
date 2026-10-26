
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text


# Obtener la carpeta generated
BASE_DIR = Path(__file__).resolve().parents[1]

# Cargar las credenciales de la base de datos de pruebas
load_dotenv(BASE_DIR / ".env.test", override=True)

# Impedir el uso de la base de datos principal
if os.getenv("DB_NAME") != "subsonic_events_test":
    raise RuntimeError(
        "ERROR: Las pruebas deben utilizar subsonic_events_test"
    )


# Importar los modulos una vez configurada la base de datos
from openapi_server.database import engine
from openapi_server.db_models import Base
from openapi_server.main import app as application
from openapi_server.models.extra_models import TokenModel
from openapi_server.security_api import get_token_BearerAuth


# Verificar la base de datos real
with engine.connect() as conexion:

    nombre_bd = conexion.execute(
        text("SELECT current_database()")
    ).scalar()

    if nombre_bd != "subsonic_events_test":
        raise RuntimeError(
            "ERROR: Conexion incorrecta. Pruebas canceladas."
        )


@pytest.fixture(scope="session", autouse=True)
def preparar_base_datos():

    # Crear las tablas necesarias para los tests
    Base.metadata.create_all(bind=engine)

    yield


# Identidad simulada para los tests funcionales
async def autenticacion_de_prueba():
    return TokenModel(sub="usr_test_555")


@pytest.fixture
def app() -> FastAPI:

    # Limpiar las modificaciones de tests anteriores
    application.dependency_overrides = {}

    # Sustituir solo durante el test la validacion externa
    application.dependency_overrides[
        get_token_BearerAuth
    ] = autenticacion_de_prueba

    yield application

    # Restaurar la aplicacion al terminar cada test
    application.dependency_overrides = {}


@pytest.fixture
def client(app) -> TestClient:

    with TestClient(app) as cliente:
        yield cliente
