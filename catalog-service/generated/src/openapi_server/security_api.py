
import os

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from openapi_server.models.extra_models import TokenModel


bearer_auth = HTTPBearer(auto_error=False)

AUTH_SERVICE_URL = os.getenv(
    "AUTH_SERVICE_URL",
    "http://127.0.0.1:8001"
).rstrip("/")


async def consultar_usuario_autenticado(
    credentials: HTTPAuthorizationCredentials
) -> dict:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="Token de autenticacion obligatorio",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Esquema de autenticacion incorrecto",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            respuesta = await client.get(
                f"{AUTH_SERVICE_URL}/users/me",
                headers={
                    "Authorization": (
                        f"Bearer {credentials.credentials}"
                    )
                }
            )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Microservicio de Autenticacion no disponible"
        ) from exc

    if respuesta.status_code in (401, 403):
        raise HTTPException(
            status_code=401,
            detail="Token invalido, caducado o revocado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if respuesta.status_code != 200:
        raise HTTPException(
            status_code=503,
            detail="No se ha podido validar la autenticacion"
        )

    try:
        usuario = respuesta.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=503,
            detail="Respuesta invalida de Autenticacion"
        ) from exc

    if (
        not isinstance(usuario, dict)
        or not isinstance(usuario.get("id"), str)
        or not usuario["id"]
        or usuario.get("role") not in (
            "client", "provider", "admin"
        )
    ):
        raise HTTPException(
            status_code=503,
            detail="Perfil recibido de Autenticacion incorrecto"
        )

    return usuario


async def get_token_BearerAuth(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_auth
    )
) -> TokenModel:
    usuario = await consultar_usuario_autenticado(
        credentials
    )

    return TokenModel(sub=usuario["id"])


async def get_admin_BearerAuth(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_auth
    )
) -> TokenModel:
    usuario = await consultar_usuario_autenticado(
        credentials
    )

    if usuario["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Se requiere rol de administrador"
        )

    return TokenModel(sub=usuario["id"])
