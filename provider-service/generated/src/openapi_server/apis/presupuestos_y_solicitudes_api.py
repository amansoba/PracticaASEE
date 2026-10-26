
import importlib
import pkgutil
from typing import List
from urllib.parse import quote

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path
)
from fastapi.security import HTTPAuthorizationCredentials

from openapi_server.apis.presupuestos_y_solicitudes_api_base import (
    BasePresupuestosYSolicitudesApi
)
from openapi_server.models.create_space_proposal_request import (
    CreateSpaceProposalRequest
)
from openapi_server.models.space_proposal import SpaceProposal
from openapi_server.models.update_proposal_status_request import (
    UpdateProposalStatusRequest
)

from openapi_server.security_api import (
    bearer_auth,
    consultar_auth,
    obtener_usuario_actual,
    obtener_usuario_proveedor,
    obtener_administrador
)
from openapi_server.event_client import consultar_evento
from openapi_server.database import SessionLocal
from openapi_server.db_models import ProviderDB

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
    if not BasePresupuestosYSolicitudesApi.subclasses:
        raise HTTPException(
            status_code=500,
            detail="API de Presupuestos no implementada"
        )

    return BasePresupuestosYSolicitudesApi.subclasses[0]()


# ============================================================
# POST /requests
# ============================================================

@router.post(
    "/requests",
    tags=["Presupuestos y Solicitudes"],
    summary="Enviar propuesta de presupuesto",
    status_code=201,
    response_model=SpaceProposal,
    responses={
        400: {"description": "Datos incorrectos"},
        401: {"description": "No autenticado"},
        403: {"description": "Proveedor sin permisos"},
        404: {"description": "Proveedor o evento inexistente"},
        409: {"description": "Conflicto de propuesta o espacio"},
        503: {"description": "Servicio externo no disponible"}
    }
)
async def create_space_proposal(
    create_space_proposal_request: CreateSpaceProposalRequest = Body(...),
    usuario_actual: dict = Depends(obtener_usuario_proveedor),
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_auth
    )
) -> SpaceProposal:

    # Validar primero los datos locales.
    from openapi_server.impl.presupuestos_y_solicitudes_impl import (
        validar_solicitud
    )

    datos = validar_solicitud(
        create_space_proposal_request
    )

    # Comprobar que la empresa existe y que pertenece
    # al usuario autenticado.
    with SessionLocal() as db:

        proveedor = db.get(
            ProviderDB,
            datos["provider_id"]
        )

        if proveedor is None:
            raise HTTPException(
                status_code=404,
                detail="Proveedor no encontrado"
            )

        if proveedor.user_id != usuario_actual["id"]:
            raise HTTPException(
                status_code=403,
                detail=(
                    "No puedes enviar propuestas "
                    "en nombre de otro proveedor"
                )
            )

    # Consulta obligatoria a Autenticacion:
    # GET /users/{userId}
    usuario_auth = await consultar_auth(
        f"/users/{quote(usuario_actual['id'], safe='')}",
        credentials.credentials
    )

    if (
        usuario_auth["id"] != usuario_actual["id"]
        or usuario_auth["role"] != "provider"
    ):
        raise HTTPException(
            status_code=403,
            detail="Identidad o rol de proveedor no valido"
        )

    if usuario_auth.get("is_active") is False:
        raise HTTPException(
            status_code=403,
            detail="Cuenta de proveedor inactiva"
        )

    # Consulta obligatoria a Eventos:
    # GET /events/{eventId}
    await consultar_evento(
        datos["event_id"]
    )

    return await obtener_implementacion().create_space_proposal(
        create_space_proposal_request,
        usuario_actual
    )


# ============================================================
# GET /requests/provider/{providerId}
# ============================================================

@router.get(
    "/requests/provider/{providerId}",
    tags=["Presupuestos y Solicitudes"],
    summary="Consultar propuestas de un proveedor",
    response_model=List[SpaceProposal],
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Acceso denegado"},
        404: {"description": "Proveedor inexistente"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def get_proposals_by_provider(
    providerId: str = Path(...),
    usuario_actual: dict = Depends(obtener_usuario_actual)
) -> List[SpaceProposal]:

    return await obtener_implementacion().get_proposals_by_provider(
        providerId,
        usuario_actual
    )


# ============================================================
# GET /requests/event/{eventId}
# ============================================================

@router.get(
    "/requests/event/{eventId}",
    tags=["Presupuestos y Solicitudes"],
    summary="Consultar presupuestos de un festival",
    response_model=List[SpaceProposal],
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def get_proposals_by_event(
    eventId: str = Path(...),
    usuario_actual: dict = Depends(obtener_administrador)
) -> List[SpaceProposal]:

    return await obtener_implementacion().get_proposals_by_event(
        eventId
    )


# ============================================================
# PUT /requests/{id}/status
# ============================================================

@router.put(
    "/requests/{id}/status",
    tags=["Presupuestos y Solicitudes"],
    summary="Aprobar o rechazar presupuesto",
    status_code=200,
    responses={
        400: {"description": "Estado incorrecto"},
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        404: {"description": "Propuesta no encontrada"},
        409: {"description": "Conflicto de adjudicacion"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def update_proposal_status(
    id: str = Path(...),
    update_proposal_status_request: UpdateProposalStatusRequest = Body(...),
    usuario_actual: dict = Depends(obtener_administrador)
) -> None:

    return await obtener_implementacion().update_proposal_status(
        id,
        update_proposal_status_request
    )
