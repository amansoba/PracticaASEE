
import os
import sys
from pathlib import Path

import pytest
from dotenv import dotenv_values
from fastapi.testclient import TestClient


# ============================================================
# CONFIGURACION DE LA BASE DE DATOS DE PRUEBAS
# ============================================================

# Carpeta commerce-service/generated
BASE_DIR = Path(__file__).resolve().parents[1]

# Cargar las variables de entorno de pruebas
configuracion = dotenv_values(BASE_DIR / ".env.test")

# Evitar utilizar accidentalmente la base de datos principal
if configuracion.get("DB_NAME") != "subsonic_commerce_test":
    raise RuntimeError(
        "ERROR: La base de datos de pruebas debe ser "
        "subsonic_commerce_test"
    )

# Aplicar las variables antes de importar la aplicacion
for clave, valor in configuracion.items():
    if valor is not None:
        os.environ[clave] = valor


# ============================================================
# CONFIGURACION DE IMPORTACIONES
# ============================================================

# Permitir importar openapi_server desde generated/src
sys.path.insert(0, str(BASE_DIR / "src"))


# ============================================================
# IMPORTAR FASTAPI Y POSTGRESQL
# ============================================================

from openapi_server.main import app
from openapi_server.database import engine
from openapi_server.db_models import Base


# ============================================================
# CLIENTE DE PRUEBAS
# ============================================================

@pytest.fixture
def client():

    # Comprobar que utilizamos exclusivamente la BD de pruebas
    if engine.url.database != "subsonic_commerce_test":
        raise RuntimeError(
            "ERROR: pytest esta intentando utilizar "
            "una base de datos que no es la de pruebas"
        )

    # Reiniciar las tablas antes de cada prueba
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Ejecutar el test mediante FastAPI TestClient
    with TestClient(app) as cliente:
        yield cliente

    # Limpiar las dependencias sobrescritas
    app.dependency_overrides.clear()
