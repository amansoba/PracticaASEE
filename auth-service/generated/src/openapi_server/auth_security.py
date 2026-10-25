
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException
from jwt import InvalidTokenError
from pwdlib import PasswordHash


# Carpeta auth-service/generated
BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


# Configuracion de tokens JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(
    os.getenv("JWT_EXPIRE_MINUTES", "60")
)

if not JWT_SECRET_KEY or len(JWT_SECRET_KEY) < 32:
    raise RuntimeError(
        "JWT_SECRET_KEY debe tener al menos 32 caracteres"
    )

if JWT_ALGORITHM != "HS256":
    raise RuntimeError(
        "Este servicio solo admite JWT_ALGORITHM=HS256"
    )

if JWT_EXPIRE_MINUTES <= 0:
    raise RuntimeError(
        "JWT_EXPIRE_MINUTES debe ser mayor que cero"
    )


# Argon2 para proteger las contrasenas
password_hasher = PasswordHash.recommended()


def cifrar_password(password: str) -> str:
    return password_hasher.hash(password)


def verificar_password(
    password: str,
    password_hash: str
) -> bool:
    return password_hasher.verify(
        password,
        password_hash
    )


def crear_token(
    user_id: str,
    role: str
) -> str:

    ahora = datetime.now(timezone.utc)
    caducidad = ahora + timedelta(
        minutes=JWT_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_id,
        "role": role,
        "iat": ahora,
        "exp": caducidad,
        "jti": uuid4().hex
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


def verificar_token(token: str) -> dict:

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={
                "require": [
                    "sub",
                    "role",
                    "iat",
                    "exp",
                    "jti"
                ]
            }
        )

    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token invalido o caducado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if (
        not isinstance(payload.get("sub"), str)
        or not payload["sub"]
        or payload.get("role") not in (
            "client",
            "provider",
            "admin"
        )
        or not isinstance(payload.get("jti"), str)
        or not payload["jti"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Contenido del token invalido",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return payload
