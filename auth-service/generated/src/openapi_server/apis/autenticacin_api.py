
# coding: utf-8

import importlib
import pkgutil

from fastapi import (
    APIRouter,
    Body,
    Header,
    HTTPException,
    Security
)
from pydantic import Field
from typing_extensions import Annotated

from openapi_server.apis.autenticacin_api_base import (
    BaseAutenticacinApi
)
from openapi_server.models.auth_response import AuthResponse
from openapi_server.models.login_request import LoginRequest
from openapi_server.models.register_request import RegisterRequest
from openapi_server.models.request_password_reset_request import (
    RequestPasswordResetRequest
)
from openapi_server.models.user_profile import UserProfile
from openapi_server.models.extra_models import TokenModel
from openapi_server.security_api import get_token_BearerAuth

import openapi_server.impl


router = APIRouter()

# Cargar las implementaciones
ns_pkg = openapi_server.impl

for _, name, _ in pkgutil.iter_modules(
    ns_pkg.__path__,
    ns_pkg.__name__ + "."
):
    importlib.import_module(name)


def obtener_implementacion():
    if not BaseAutenticacinApi.subclasses:
        raise HTTPException(
            status_code=500,
            detail="Autenticacion API no implementada"
        )

    return BaseAutenticacinApi.subclasses[0]()


# POST /auth/register
@router.post(
    "/auth/register",
    status_code=201,
    responses={
        201: {
            "model": UserProfile,
            "description": "Usuario registrado exitosamente."
        },
        400: {
            "description": "Datos invalidos o correo ya registrado."
        }
    },
    tags=["Autenticacion"],
    summary="Registrar un nuevo usuario",
    response_model=UserProfile,
    response_model_by_alias=True
)
async def register_user(
    register_request: Annotated[
        RegisterRequest,
        Field(description="Datos de registro.")
    ] = Body(...)
) -> UserProfile:

    return await obtener_implementacion().register_user(
        register_request
    )


# POST /auth/login
@router.post(
    "/auth/login",
    responses={
        200: {
            "model": AuthResponse,
            "description": "Autenticacion exitosa."
        },
        401: {
            "description": "Credenciales incorrectas."
        }
    },
    tags=["Autenticacion"],
    summary="Iniciar sesion",
    response_model=AuthResponse,
    response_model_by_alias=True
)
async def login_user(
    login_request: Annotated[
        LoginRequest,
        Field(description="Credenciales de acceso.")
    ] = Body(...)
) -> AuthResponse:

    return await obtener_implementacion().login_user(
        login_request
    )


# POST /auth/logout
@router.post(
    "/auth/logout",
    responses={
        200: {
            "description": "Sesion cerrada correctamente."
        },
        401: {
            "description": "Token no proporcionado o invalido."
        }
    },
    tags=["Autenticacion"],
    summary="Cerrar sesion"
)
async def logout_user(
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    ),
    authorization: str | None = Header(
        default=None
    )
) -> None:

    # Security valida previamente la firma, caducidad,
    # existencia del usuario y revocacion del JWT.
    # Aqui recuperamos el token original para revocarlo.

    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Token obligatorio"
        )

    partes = authorization.split()

    if (
        len(partes) != 2
        or partes[0].lower() != "bearer"
        or not partes[1]
    ):
        raise HTTPException(
            status_code=401,
            detail="Formato de autorizacion incorrecto"
        )

    token = partes[1]

    return await obtener_implementacion().logout_user(
        token
    )


# POST /auth/reset-password
@router.post(
    "/auth/reset-password",
    responses={
        200: {
            "description": "Solicitud de recuperacion procesada."
        },
        503: {
            "description": "Servicio de correo no disponible."
        }
    },
    tags=["Autenticacion"],
    summary="Solicitar recuperacion de contrasena"
)
async def request_password_reset(
    request_password_reset_request: Annotated[
        RequestPasswordResetRequest,
        Field(description="Correo de la cuenta.")
    ] = Body(...)
) -> None:

    return await obtener_implementacion().request_password_reset(
        request_password_reset_request
    )
