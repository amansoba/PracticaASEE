
import os

import httpx

from fastapi import Depends, HTTPException, Request
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from openapi_server.models.extra_models import TokenModel


bearer_auth = HTTPBearer(auto_error=False)


async def get_token_BearerAuth(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_auth
    )
) -> TokenModel:

    # Comprobar que se ha enviado un token Bearer
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="Token de autenticacion obligatorio",
            headers={"WWW-Authenticate": "Bearer"}
        )

    auth_url = os.getenv("AUTH_SERVICE_URL")

    if not auth_url:
        raise HTTPException(
            status_code=503,
            detail="Servicio de autenticacion no configurado"
        )

    # Delegar la validacion del token en auth-service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            respuesta = await client.get(
                f"{auth_url.rstrip('/')}/users/me",
                headers={
                    "Authorization": (
                        f"Bearer {credentials.credentials}"
                    )
                }
            )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Servicio de autenticacion no disponible"
        )

    if respuesta.status_code in (401, 403):
        raise HTTPException(
            status_code=401,
            detail="Token invalido o caducado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if respuesta.status_code != 200:
        raise HTTPException(
            status_code=503,
            detail="No se pudo verificar el token"
        )

    try:
        usuario = respuesta.json()
    except ValueError:
        raise HTTPException(
            status_code=503,
            detail="Respuesta invalida de autenticacion"
        )

    if not isinstance(usuario, dict):
        raise HTTPException(
            status_code=503,
            detail="Perfil de usuario invalido"
        )

    usuario_id = usuario.get("id")
    rol = usuario.get("role")

    if (
        not isinstance(usuario_id, str)
        or not usuario_id
        or rol not in ("client", "provider", "admin")
    ):
        raise HTTPException(
            status_code=503,
            detail="Perfil de usuario incompleto"
        )

    ruta = request.url.path
    metodo = request.method

    # Gestion administrativa de festivales y pases
    es_operacion_administrativa = (
        (ruta == "/events" and metodo == "POST")
        or (
            ruta.startswith("/events/")
            and metodo in ("PUT", "DELETE")
        )
        or (
            ruta.startswith("/events/")
            and ruta.endswith("/lineup")
            and metodo == "POST"
        )
        or (
            ruta.startswith("/events/")
            and ruta.endswith("/passes")
            and metodo == "POST"
        )
    )

    if es_operacion_administrativa and rol != "admin":
        raise HTTPException(
            status_code=403,
            detail="Se requiere rol de administrador"
        )

    # Cada usuario solo puede consultar sus entradas
    if (
        ruta.startswith("/tickets/user/")
        and metodo == "GET"
    ):
        propietario_id = ruta.removeprefix("/tickets/user/")

        if rol != "admin" and propietario_id != usuario_id:
            raise HTTPException(
                status_code=403,
                detail="No puedes consultar entradas de otro usuario"
            )

    # Impedir compras asignadas a un usuario diferente
    if ruta == "/tickets/purchase" and metodo == "POST":

        try:
            cuerpo = await request.json()
        except ValueError:
            cuerpo = None

        if isinstance(cuerpo, dict):
            comprador_id = cuerpo.get("user_id")

            if (
                comprador_id is not None
                and comprador_id != usuario_id
                and rol != "admin"
            ):
                raise HTTPException(
                    status_code=403,
                    detail="No puedes comprar entradas para otro usuario"
                )

    return TokenModel(sub=usuario_id)
