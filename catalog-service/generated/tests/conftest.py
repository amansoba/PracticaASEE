
import os
import sys
from pathlib import Path

import pytest
from dotenv import dotenv_values
from fastapi.testclient import TestClient


# Directorios del proyecto
BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"

sys.path.insert(0, str(SRC_DIR))


# Cargar exclusivamente la configuracion de pruebas
config = dotenv_values(BASE_DIR / ".env.test")

if not config:
    raise RuntimeError(
        "No existe .env.test o esta vacio"
    )

if config.get("DB_NAME") != "subsonic_catalog_test":
    raise RuntimeError(
        "Los tests solo pueden usar subsonic_catalog_test"
    )

for clave, valor in config.items():
    if valor is not None:
        os.environ[clave] = valor


# Importar despues de configurar las variables
from openapi_server.main import app
from openapi_server.database import engine
from openapi_server.db_models import Base

# Importar ambos modelos para registrar sus tablas
from openapi_server.db_models import ArtistDB, SongDB


@pytest.fixture
def client():
    # Evitar borrar tablas de otra base de datos
    if engine.url.database != "subsonic_catalog_test":
        raise RuntimeError(
            "Conexion incorrecta: se esperaba subsonic_catalog_test"
        )

    # Limpiar las tablas antes de cada prueba
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as cliente:
        yield cliente

    # Limpiar despues de cada prueba
    Base.metadata.drop_all(bind=engine)
