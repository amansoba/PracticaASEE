# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.line_up_api_base import BaseLineUpApi
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
from openapi_server.models.create_schedule_entry_request import CreateScheduleEntryRequest
from openapi_server.models.schedule_entry import ScheduleEntry
from openapi_server.models.extra_models import TokenModel  # noqa: F401
from openapi_server.security_api import get_token_BearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/events/{id}/lineup",
    responses={
        200: {"model": List[ScheduleEntry], "description": "Horarios y cartel devueltos con éxito."},
        404: {"description": "El evento especificado no existe."},
    },
    tags=["Line-up"],
    summary="Obtener el cartel (Line-up) y horarios del festival",
    response_model_by_alias=True,
)
async def get_event_lineup(
    id: Annotated[str, Field(description="Identificador del evento.")] = Path(..., description="Identificador del evento.", examples=["evt_101"]),
) -> List[ScheduleEntry]:
    """Devuelve las actuaciones programadas en los escenarios y sus franjas horarias. """
    if not BaseLineUpApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseLineUpApi.subclasses[0]().get_event_lineup(id)


@router.post(
    "/events/{id}/lineup",
    responses={
        201: {"model": ScheduleEntry, "description": "Actuación añadida al cartel correctamente."},
        400: {"description": "Solapamiento horario o datos incorrectos."},
        401: {"description": "No autenticado."},
        403: {"description": "Acceso denegado."},
        404: {"description": "El evento o el artista no existen. Este error puede producirse si la consulta síncrona a Catálogo Musical devuelve un 404. "},
        503: {"description": "No se pudo validar el artista porque el microservicio de Catálogo Musical no se encuentra disponible. "},
    },
    tags=["Line-up"],
    summary="Añadir una actuación al line-up del evento",
    response_model_by_alias=True,
)
async def add_schedule_entry(
    id: Annotated[str, Field(description="Identificador del evento al que se añade la actuación.")] = Path(..., description="Identificador del evento al que se añade la actuación.", examples=["evt_101"]),
    create_schedule_entry_request: Annotated[CreateScheduleEntryRequest, Field(description="Datos del artista, escenario y horario.")] = Body(..., description="Datos del artista, escenario y horario."),
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    ),
) -> ScheduleEntry:
    """Registra la actuación de un artista en un escenario y franja horaria. Antes de crear la entrada, este microservicio realiza una COMUNICACIÓN SÍNCRONA de tipo CONSULTA: Gestión de Eventos -&gt; Catálogo Musical -&gt; GET /artists/{artistId} para validar que el artista existe en el catálogo musical. """
    if not BaseLineUpApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseLineUpApi.subclasses[0]().add_schedule_entry(id, create_schedule_entry_request)
