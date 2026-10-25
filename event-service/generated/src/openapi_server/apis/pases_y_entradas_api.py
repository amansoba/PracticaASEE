# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.pases_y_entradas_api_base import BasePasesYEntradasApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from pydantic import Field
from typing import Any, List
from typing_extensions import Annotated
from openapi_server.models.create_pass_config_request import CreatePassConfigRequest
from openapi_server.models.pass_config import PassConfig
from openapi_server.models.ticket import Ticket
from openapi_server.models.ticket_purchase_request import TicketPurchaseRequest
from openapi_server.models.extra_models import TokenModel  # noqa: F401
from openapi_server.security_api import get_token_BearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/events/{id}/passes",
    responses={
        200: {"model": List[PassConfig], "description": "Tipos de pases configurados."},
        404: {"description": "Evento no encontrado."},
    },
    tags=["Pases y Entradas"],
    summary="Consultar los tipos de pases y aforo configurado",
    response_model_by_alias=True,
)
async def get_pass_configs_by_event(
    id: Annotated[str, Field(description="Identificador del evento.")] = Path(..., description="Identificador del evento.", examples=["evt_101"]),
) -> List[PassConfig]:
    """Devuelve los tipos de entrada disponibles para el evento (general, VIP, abono). """
    if not BasePasesYEntradasApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePasesYEntradasApi.subclasses[0]().get_pass_configs_by_event(id)


@router.post(
    "/events/{id}/passes",
    responses={
        201: {"model": PassConfig, "description": "Modalidad de pase dada de alta exitosamente."},
        401: {"description": "No autenticado."},
        403: {"description": "Acceso denegado."},
    },
    tags=["Pases y Entradas"],
    summary="Configurar un nuevo tipo de pase para el evento",
    response_model_by_alias=True,
)
async def create_pass_config(
    id: Annotated[str, Field(description="Identificador del evento al que se asigna la entrada.")] = Path(..., description="Identificador del evento al que se asigna la entrada.", examples=["evt_101"]),
    create_pass_config_request: Annotated[CreatePassConfigRequest, Field(description="Configuración del pase y aforo.")] = Body(..., description="Configuración del pase y aforo."),
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    ),
) -> PassConfig:
    """Define precio, aforo máximo y beneficios de una modalidad de entrada. Operación para administradores. """
    if not BasePasesYEntradasApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePasesYEntradasApi.subclasses[0]().create_pass_config(id, create_pass_config_request)


@router.post(
    "/tickets/purchase",
    responses={
        201: {"model": Ticket, "description": "Entrada emitida y asociada exitosamente al usuario."},
        400: {"description": "Datos de compra incompletos."},
        401: {"description": "No autenticado."},
        404: {"description": "El usuario indicado no existe según la consulta a Autenticación y Cuentas, o el tipo de pase seleccionado no existe. "},
        409: {"description": "Aforo máximo completado. No quedan entradas disponibles para este pase."},
        503: {"description": "No se pudo verificar la identidad del comprador porque el microservicio de Autenticación y Cuentas no está disponible. "},
    },
    tags=["Pases y Entradas"],
    summary="Comprar una entrada / pase para un evento",
    response_model_by_alias=True,
)
async def purchase_ticket(
    ticket_purchase_request: Annotated[TicketPurchaseRequest, Field(description="Identificadores del evento, tipo de pase, usuario y token de pago.")] = Body(..., description="Identificadores del evento, tipo de pase, usuario y token de pago."),
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    ),
) -> Ticket:
    """Emite una entrada nominal y decrementa el aforo del pase. Antes de emitir la entrada, este microservicio realiza una COMUNICACIÓN SÍNCRONA de tipo CONSULTA: Gestión de Eventos -&gt; Autenticación y Cuentas -&gt; GET /users/{userId} para validar la identidad del comprador y asociar la entrada a su propietario. """
    if not BasePasesYEntradasApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePasesYEntradasApi.subclasses[0]().purchase_ticket(ticket_purchase_request)


@router.get(
    "/tickets/user/{userId}",
    responses={
        200: {"model": List[Ticket], "description": "Entradas del usuario."},
        401: {"description": "No autenticado."},
        403: {"description": "Acceso denegado. No se pueden consultar entradas de otro usuario."},
    },
    tags=["Pases y Entradas"],
    summary="Consultar las entradas adquiridas por un usuario",
    response_model_by_alias=True,
)
async def get_tickets_by_user(
    userId: Annotated[str, Field(description="Identificador del usuario propietario de las entradas.")] = Path(..., description="Identificador del usuario propietario de las entradas.", examples=["usr_555"]),
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    ),
) -> List[Ticket]:
    """Devuelve el listado de entradas emitidas asociadas al identificador del comprador. """
    if not BasePasesYEntradasApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePasesYEntradasApi.subclasses[0]().get_tickets_by_user(userId)
