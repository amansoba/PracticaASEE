
import os
import sys
from pathlib import Path

# Localizar las carpetas del proyecto
BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"

sys.path.insert(0, str(SRC_DIR))

# Cargar las variables de la base de datos de pruebas
from dotenv import dotenv_values

config = dotenv_values(BASE_DIR / ".env.test")

if not config:
    raise RuntimeError(
        "No se ha encontrado .env.test"
    )

if config.get("DB_NAME") != "subsonic_auth_test":
    raise RuntimeError(
        "Los tests solo pueden usar subsonic_auth_test"
    )

# Sobrescribir la configuracion antes de importar FastAPI
for clave, valor in config.items():
    if valor is not None:
        os.environ[clave] = valor

os.environ["JWT_SECRET_KEY"] = (
    "clave-exclusiva-para-pruebas-subsonic-2026-"
    "no-utilizar-en-produccion"
)

os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_EXPIRE_MINUTES"] = "60"


# Importar la aplicacion despues de configurar el entorno
import pytest
from fastapi.testclient import TestClient

from openapi_server.main import app
from openapi_server.database import engine
from openapi_server.db_models import Base, UserDB
import openapi_server.auth_flows


@pytest.fixture
def client():
    # Comprobar nuevamente la base de datos activa
    if engine.url.database != "subsonic_auth_test":
        raise RuntimeError(
            "Conexion incorrecta: se esperaba subsonic_auth_test"
        )

    # Crear tablas y preparar una base limpia para cada test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as cliente:
        yield cliente

    Base.metadata.drop_all(bind=engine)
