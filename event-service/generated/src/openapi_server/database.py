
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker


# Localizar el archivo .env del proyecto
BASE_DIR = Path(__file__).resolve().parents[2]

# Cargar las variables de entorno
load_dotenv(BASE_DIR / ".env")

# Construir la conexion a PostgreSQL
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME"),
)

# Crear el motor de conexion
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Crear sesiones de base de datos
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


def comprobar_conexion():
    """Comprueba que PostgreSQL acepta conexiones."""
    with engine.connect() as conexion:
        resultado = conexion.execute(
            text("SELECT current_database()")
        )
        return resultado.scalar()
