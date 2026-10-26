
import importlib
import pkgutil
from typing import List

from fastapi import (
    APIRouter,
    Body,
    HTTPException,
    Path,
    Security
)
from pydantic import Field
from typing_extensions import Annotated

from openapi_server.apis.usuarios_api_base import BaseUsuariosApi
from openapi_server.models.update_profile_request import (
    UpdateProfileRequest
)
from openapi_server.models.update_user_role_request import (
    UpdateUserRoleRequest
)
from openapi_server.models.user_profile import UserProfile
from openapi_server.models.extra_models import TokenModel
from openapi_server.security_api import get_token_BearerAuth

import openapi_server.impl


router = APIRouter()

# Cargar las implementaciones del microservicio
ns_pkg = openapi_server.impl

for _, name, _ in pkgutil.iter_modules(
    ns_pkg.__path__,
    ns_pkg.__name__ + "."
):
    importlib.import_module(name)


def obtener_implementacion():
    if not BaseUsuariosApi.subclasses:
        raise HTTPException(
            status_code=500,
            detail="Usuarios API no implementada"
        )

    return BaseUsuariosApi.subclasses[0]()


# GET /users/me
@router.get(
    "/users/me",
    responses={
        200: {
            "model": UserProfile,
            "description": "Perfil del usuario autenticado."
        },
        401: {
            "description": "Token invalido o ausente."
        }
    },
    tags=["Usuarios"],
    summary="Obtener el perfil del usuario autenticado",
    response_model=UserProfile,
    response_model_by_alias=True
)
async def get_current_user_profile(
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    )
) -> UserProfile:

    return await obtener_implementacion().get_current_user_profile(
        token_BearerAuth.sub
    )


# PUT /users/me
@router.put(
    "/users/me",
    responses={
        200: {
            "model": UserProfile,
            "description": "Perfil actualizado."
        },
        400: {
            "description": "Datos incorrectos."
        },
        401: {
            "description": "No autenticado."
        }
    },
    tags=["Usuarios"],
    summary="Actualizar el perfil del usuario autenticado",
    response_model=UserProfile,
    response_model_by_alias=True
)
async def update_current_user_profile(
    update_profile_request: Annotated[
        UpdateProfileRequest,
        Field(description="Campos de perfil a actualizar.")
    ] = Body(...),
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    )
) -> UserProfile:

    return await obtener_implementacion().update_current_user_profile(
        update_profile_request,
        token_BearerAuth.sub
    )


# GET /users
@router.get(
    "/users",
    responses={
        200: {
            "model": List[UserProfile],
            "description": "Listado de usuarios."
        },
        401: {
            "description": "No autenticado."
        },
        403: {
            "description": "Se requiere rol de administrador."
        }
    },
    tags=["Usuarios"],
    summary="Listar todos los usuarios",
    response_model=List[UserProfile],
    response_model_by_alias=True
)
async def list_all_users(
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    )
) -> List[UserProfile]:

    return await obtener_implementacion().list_all_users(
        token_BearerAuth.sub
    )


# GET /users/{id}
@router.get(
    "/users/{id}",
    responses={
        200: {
            "model": UserProfile,
            "description": "Usuario encontrado."
        },
        401: {
            "description": "No autenticado."
        },
        404: {
            "description": "Usuario no encontrado."
        }
    },
    tags=["Usuarios"],
    summary="Consultar un usuario por identificador",
    response_model=UserProfile,
    response_model_by_alias=True
)
async def get_user_by_id(
    id: Annotated[
        str,
        Field(description="Identificador del usuario.")
    ] = Path(...),
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    )
) -> UserProfile:

    return await obtener_implementacion().get_user_by_id(
        id,
        token_BearerAuth.sub
    )


# PUT /users/{id}/role
@router.put(
    "/users/{id}/role",
    responses={
        200: {
            "description": "Rol modificado correctamente."
        },
        401: {
            "description": "No autenticado."
        },
        403: {
            "description": "Se requiere rol de administrador."
        },
        404: {
            "description": "Usuario no encontrado."
        }
    },
    tags=["Usuarios"],
    summary="Modificar el rol de un usuario",
    status_code=200
)
async def update_user_role(
    id: Annotated[
        str,
        Field(description="Identificador del usuario.")
    ] = Path(...),
    update_user_role_request: Annotated[
        UpdateUserRoleRequest,
        Field(description="Nuevo rol del usuario.")
    ] = Body(...),
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    )
) -> None:

    return await obtener_implementacion().update_user_role(
        id,
        update_user_role_request,
        token_BearerAuth.sub
    )
