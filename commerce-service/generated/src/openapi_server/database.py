
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker


# Carpeta commerce-service/generated
BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


# Configuracion de PostgreSQL
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME")
)


# Motor de conexion con PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# Sesiones de base de datos
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
