
import importlib
import pkgutil
from typing import List

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Query
)

from openapi_server.apis.servicios_y_espacios_api_base import (
    BaseServiciosYEspaciosApi
)

from openapi_server.models.create_external_service_request import (
    CreateExternalServiceRequest
)
from openapi_server.models.create_space_request import (
    CreateSpaceRequest
)
from openapi_server.models.external_service import ExternalService
from openapi_server.models.space import Space

from openapi_server.security_api import obtener_administrador
from openapi_server.event_client import consultar_evento

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
    if not BaseServiciosYEspaciosApi.subclasses:
        raise HTTPException(
            status_code=500,
            detail="API de Servicios y Espacios no implementada"
        )

    return BaseServiciosYEspaciosApi.subclasses[0]()


# ============================================================
# GET /external-services
# ============================================================

@router.get(
    "/external-services",
    tags=["Servicios y Espacios"],
    summary="Consultar catalogo de servicios externos",
    response_model=List[ExternalService]
)
async def get_external_services() -> List[ExternalService]:

    return await obtener_implementacion().get_external_services()


# ============================================================
# POST /external-services
# ============================================================

@router.post(
    "/external-services",
    tags=["Servicios y Espacios"],
    summary="Crear un servicio externo",
    status_code=201,
    response_model=ExternalService,
    responses={
        400: {"description": "Datos invalidos"},
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def create_external_service(
    create_external_service_request: CreateExternalServiceRequest = Body(...),
    usuario_actual: dict = Depends(obtener_administrador)
) -> ExternalService:

    return await obtener_implementacion().create_external_service(
        create_external_service_request
    )


# ============================================================
# GET /spaces
# ============================================================

@router.get(
    "/spaces",
    tags=["Servicios y Espacios"],
    summary="Consultar espacios de un evento",
    response_model=List[Space],
    responses={
        400: {"description": "Evento no valido"}
    }
)
async def get_spaces_by_event(
    event_id: str = Query(
        ...,
        description="Identificador del evento"
    )
) -> List[Space]:

    return await obtener_implementacion().get_spaces_by_event(
        event_id
    )


# ============================================================
# POST /spaces
# ============================================================

@router.post(
    "/spaces",
    tags=["Servicios y Espacios"],
    summary="Publicar espacio alquilable",
    status_code=201,
    response_model=Space,
    responses={
        400: {"description": "Datos invalidos"},
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        404: {"description": "Evento no encontrado"},
        409: {"description": "Espacio duplicado"},
        503: {"description": "Servicio externo no disponible"}
    }
)
async def create_space(
    create_space_request: CreateSpaceRequest = Body(...),
    usuario_actual: dict = Depends(obtener_administrador)
) -> Space:

    from openapi_server.impl.servicios_y_espacios_impl import (
        validar_espacio
    )

    validar_espacio(create_space_request)

    # Verificar que el festival existe.
    await consultar_evento(
        create_space_request.event_id
    )

    return await obtener_implementacion().create_space(
        create_space_request
    )
