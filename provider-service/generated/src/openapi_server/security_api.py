
import os
from pathlib import Path
from urllib.parse import quote

import httpx
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from openapi_server.models.extra_models import TokenModel


# ============================================================
# CONFIGURACION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")

AUTH_SERVICE_URL = os.getenv(
    "AUTH_SERVICE_URL",
    "http://127.0.0.1:8001"
).rstrip("/")

bearer_auth = HTTPBearer(
    scheme_name="BearerAuth",
    auto_error=False
)


# ============================================================
# ERRORES DE AUTENTICACION
# ============================================================

def error_token():
    return HTTPException(
        status_code=401,
        detail="Token invalido, caducado o revocado",
        headers={"WWW-Authenticate": "Bearer"}
    )


# ============================================================
# COMUNICACION CON AUTH-SERVICE
# ============================================================

async def consultar_auth(ruta: str, token: str) -> dict:
    """
    Consulta auth-service utilizando el token JWT original.
    La validacion del token se delega en Autenticacion.
    """

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            respuesta = await client.get(
                f"{AUTH_SERVICE_URL}{ruta}",
                headers={
                    "Authorization": f"Bearer {token}"
                }
            )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Microservicio de Autenticacion no disponible"
        ) from exc

    if respuesta.status_code in (401, 403):
        raise error_token()

    if respuesta.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado en Autenticacion"
        )

    if respuesta.status_code != 200:
        raise HTTPException(
            status_code=503,
            detail="No se ha podido consultar Autenticacion"
        )

    try:
        usuario = respuesta.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=503,
            detail="Respuesta incorrecta de Autenticacion"
        ) from exc

    if (
        not isinstance(usuario, dict)
        or not isinstance(usuario.get("id"), str)
        or not usuario["id"]
        or usuario.get("role") not in (
            "client",
            "provider",
            "admin"
        )
    ):
        raise HTTPException(
            status_code=503,
            detail="Perfil de usuario incorrecto"
        )

    return usuario


# ============================================================
# USUARIO AUTENTICADO
# ============================================================

async def obtener_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_auth
    )
) -> dict:

    if (
        credentials is None
        or credentials.scheme.lower() != "bearer"
        or not credentials.credentials
    ):
        raise HTTPException(
            status_code=401,
            detail="Token Bearer obligatorio",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return await consultar_auth(
        "/users/me",
        credentials.credentials
    )


# ============================================================
# ADMINISTRADORES
# ============================================================

async def obtener_administrador(
    usuario: dict = Depends(obtener_usuario_actual)
) -> dict:

    if usuario["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Se requiere rol de administrador"
        )

    return usuario


# ============================================================
# PROVEEDORES
# ============================================================

async def obtener_usuario_proveedor(
    usuario: dict = Depends(obtener_usuario_actual)
) -> dict:

    if usuario["role"] != "provider":
        raise HTTPException(
            status_code=403,
            detail="Se requiere rol de proveedor"
        )

    return usuario


# ============================================================
# VALIDAR REGISTRO CON AUTH-SERVICE
# ============================================================

async def validar_registro_proveedor(
    user_id: str,
    usuario_actual: dict,
    credentials: HTTPAuthorizationCredentials
) -> dict:
    """
    Comprueba la identidad del solicitante y realiza
    la consulta obligatoria GET /users/{userId}.
    """

    if usuario_actual["id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail=(
                "No puedes registrar una empresa "
                "en nombre de otro usuario"
            )
        )

    if usuario_actual["role"] != "provider":
        raise HTTPException(
            status_code=403,
            detail="Se requiere rol de proveedor"
        )

    usuario = await consultar_auth(
        f"/users/{quote(user_id, safe='')}",
        credentials.credentials
    )

    if usuario["id"] != user_id:
        raise HTTPException(
            status_code=503,
            detail="Identidad inconsistente en Autenticacion"
        )

    if usuario["role"] != "provider":
        raise HTTPException(
            status_code=403,
            detail="El usuario no tiene rol de proveedor"
        )

    # Si auth-service informa explicitamente de que la
    # cuenta esta inactiva, impedir el registro.
    if usuario.get("is_active") is False:
        raise HTTPException(
            status_code=403,
            detail="La cuenta del proveedor esta inactiva"
        )

    return usuario


# ============================================================
# COMPATIBILIDAD CON OPENAPI GENERATOR
# ============================================================

async def get_token_BearerAuth(
    usuario: dict = Depends(obtener_usuario_actual)
) -> TokenModel:

    return TokenModel(
        sub=usuario["id"]
    )
