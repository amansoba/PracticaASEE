
import importlib
import pkgutil
from typing import List

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path
)

from fastapi.security import HTTPAuthorizationCredentials

from openapi_server.apis.proveedores_api_base import (
    BaseProveedoresApi
)

from openapi_server.models.create_provider_request import (
    CreateProviderRequest
)

from openapi_server.models.provider_profile import (
    ProviderProfile
)

from openapi_server.security_api import (
    bearer_auth,
    obtener_usuario_actual,
    obtener_administrador,
    obtener_usuario_proveedor,
    validar_registro_proveedor
)

import openapi_server.impl


# ============================================================
# CONFIGURACION DEL ROUTER
# ============================================================

router = APIRouter()

ns_pkg = openapi_server.impl

for _, name, _ in pkgutil.iter_modules(
    ns_pkg.__path__,
    ns_pkg.__name__ + "."
):
    importlib.import_module(name)


def obtener_implementacion():
    if not BaseProveedoresApi.subclasses:
        raise HTTPException(
            status_code=500,
            detail="API de Proveedores no implementada"
        )

    return BaseProveedoresApi.subclasses[0]()


# ============================================================
# GET /providers
# ============================================================

@router.get(
    "/providers",
    tags=["Proveedores"],
    summary="Listar proveedores registrados",
    response_model=List[ProviderProfile],
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def get_providers(
    usuario_actual: dict = Depends(obtener_administrador)
) -> List[ProviderProfile]:

    return await obtener_implementacion().get_providers()


# ============================================================
# POST /providers
# ============================================================

@router.post(
    "/providers",
    tags=["Proveedores"],
    summary="Registrar ficha de proveedor",
    status_code=201,
    response_model=ProviderProfile,
    responses={
        400: {"description": "Datos invalidos"},
        401: {"description": "No autenticado"},
        403: {"description": "Sin permisos de proveedor"},
        404: {"description": "Usuario no encontrado"},
        409: {"description": "Proveedor duplicado"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def create_provider(
    create_provider_request: CreateProviderRequest = Body(...),
    usuario_actual: dict = Depends(obtener_usuario_proveedor),
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_auth
    )
) -> ProviderProfile:

    # Comprobar propietario y rol mediante auth-service.
    await validar_registro_proveedor(
        create_provider_request.user_id,
        usuario_actual,
        credentials
    )

    return await obtener_implementacion().create_provider(
        create_provider_request
    )


# ============================================================
# GET /providers/{id}
# ============================================================

@router.get(
    "/providers/{id}",
    tags=["Proveedores"],
    summary="Consultar detalle de un proveedor",
    response_model=ProviderProfile,
    responses={
        401: {"description": "No autenticado"},
        404: {"description": "Proveedor no encontrado"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def get_provider_by_id(
    id: str = Path(...),
    usuario_actual: dict = Depends(obtener_usuario_actual)
) -> ProviderProfile:

    return await obtener_implementacion().get_provider_by_id(
        id
    )
