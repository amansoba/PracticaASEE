
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from openapi_server.models.extra_models import TokenModel


# Carpeta commerce-service/generated
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

AUTH_SERVICE_URL = os.getenv(
    "AUTH_SERVICE_URL",
    "http://127.0.0.1:8001"
).rstrip("/")

bearer_auth = HTTPBearer(auto_error=False)


def error_autenticacion():
    return HTTPException(
        status_code=401,
        detail="Token invalido, caducado o revocado",
        headers={"WWW-Authenticate": "Bearer"}
    )


async def consultar_auth(
    ruta: str,
    token: str
) -> dict:
    """
    Consulta al microservicio de Autenticacion
    utilizando el JWT original del usuario.
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
        raise error_autenticacion()

    if respuesta.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado en Autenticacion"
        )

    if respuesta.status_code != 200:
        raise HTTPException(
            status_code=503,
            detail="No se ha podido validar el usuario"
        )

    try:
        datos = respuesta.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=503,
            detail="Respuesta incorrecta de Autenticacion"
        ) from exc

    if (
        not isinstance(datos, dict)
        or not isinstance(datos.get("id"), str)
        or not datos["id"]
        or datos.get("role") not in (
            "client", "provider", "admin"
        )
    ):
        raise HTTPException(
            status_code=503,
            detail="Perfil recibido de Autenticacion incorrecto"
        )

    return datos


async def obtener_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_auth
    )
) -> dict:
    """
    Valida el JWT consultando GET /users/me.
    No confiamos en roles enviados por el cliente.
    """
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


async def obtener_administrador(
    usuario: dict = Depends(obtener_usuario_actual)
) -> dict:
    if usuario["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Se requiere rol de administrador"
        )

    return usuario


async def validar_comprador(
    user_id: str,
    credentials: HTTPAuthorizationCredentials
) -> dict:
    """
    Consulta GET /users/{id}, tal como exige
    el contrato OpenAPI de Tienda.

    Comprueba que el usuario del pedido coincide
    con el propietario del JWT.
    """
    usuario = await consultar_auth(
        f"/users/{user_id}",
        credentials.credentials
    )

    if usuario["id"] != user_id:
        raise HTTPException(
            status_code=503,
            detail="Identidad inconsistente en Autenticacion"
        )

    return usuario


# Compatibilidad con el esquema BearerAuth generado.
async def get_token_BearerAuth(
    usuario: dict = Depends(obtener_usuario_actual)
) -> TokenModel:
    return TokenModel(sub=usuario["id"])
