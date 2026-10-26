# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.eventos_api_base import BaseEventosApi
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
from openapi_server.models.create_event_request import CreateEventRequest
from openapi_server.models.event import Event
from openapi_server.models.extra_models import TokenModel  # noqa: F401
from openapi_server.security_api import get_token_BearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/events",
    responses={
        200: {"model": List[Event], "description": "Lista de eventos devuelta correctamente."},
    },
    tags=["Eventos"],
    summary="Listar todos los festivales y eventos",
    response_model_by_alias=True,
)
async def get_all_events(
) -> List[Event]:
    """Devuelve la lista general de eventos y ediciones de festivales configurados. """
    if not BaseEventosApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseEventosApi.subclasses[0]().get_all_events()


@router.post(
    "/events",
    status_code=201,
    responses={
        201: {"model": Event, "description": "Evento registrado exitosamente."},
        400: {"description": "Datos del evento incompletos."},
        401: {"description": "No autenticado."},
        403: {"description": "Acceso denegado. Requiere rol de administrador."},
    },
    tags=["Eventos"],
    summary="Crear un nuevo evento o edición",
    response_model_by_alias=True,
)
async def create_event(
    create_event_request: Annotated[CreateEventRequest, Field(description="Información básica del evento.")] = Body(..., description="Información básica del evento."),
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    ),
) -> Event:
    """Da de alta un festival indicando nombre, fechas y recinto. Operación restringida a administradores. """
    if not BaseEventosApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseEventosApi.subclasses[0]().create_event(create_event_request)


@router.get(
    "/events/{id}",
    responses={
        200: {"model": Event, "description": "Detalles del evento."},
        404: {"description": "No existe ningún evento con el identificador proporcionado."},
    },
    tags=["Eventos"],
    summary="Consultar detalles de un evento",
    response_model_by_alias=True,
)
async def get_event_by_id(
    id: Annotated[str, Field(description="Identificador único del evento.")] = Path(..., description="Identificador único del evento.", examples=["evt_101"]),
) -> Event:
    """Devuelve las fechas, recinto y ubicación de un festival. Endpoint consultado de forma síncrona por Gestión de Proveedores para asociar espacios y servicios. """
    if not BaseEventosApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseEventosApi.subclasses[0]().get_event_by_id(id)


@router.put(
    "/events/{id}",
    responses={
        200: {"model": Event, "description": "Evento actualizado correctamente."},
        401: {"description": "No autenticado."},
        403: {"description": "Acceso denegado."},
        404: {"description": "Evento no encontrado."},
    },
    tags=["Eventos"],
    summary="Actualizar información de un evento",
    response_model_by_alias=True,
)
async def update_event(
    id: Annotated[str, Field(description="Identificador del evento a actualizar.")] = Path(..., description="Identificador del evento a actualizar.", examples=["evt_101"]),
    create_event_request: Annotated[CreateEventRequest, Field(description="Nuevos datos del evento.")] = Body(..., description="Nuevos datos del evento."),
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    ),
) -> Event:
    """Permite actualizar fechas o recintos de un evento existente. Operación para administradores. """
    if not BaseEventosApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseEventosApi.subclasses[0]().update_event(id, create_event_request)


@router.delete(
    "/events/{id}",
    status_code=204,
    responses={
        204: {"description": "Evento eliminado satisfactoriamente."},
        401: {"description": "No autenticado."},
        403: {"description": "Acceso denegado."},
        404: {"description": "Evento no encontrado."},
    },
    tags=["Eventos"],
    summary="Cancelar o eliminar un evento",
    response_model_by_alias=True,
)
async def delete_event(
    id: Annotated[str, Field(description="Identificador del evento a cancelar.")] = Path(..., description="Identificador del evento a cancelar.", examples=["evt_101"]),
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    ),
) -> None:
    """Elimina un festival del sistema. Operación para administradores. """
    if not BaseEventosApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseEventosApi.subclasses[0]().delete_event(id)
