# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.canciones_api_base import BaseCancionesApi
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
from openapi_server.models.create_song_request import CreateSongRequest
from openapi_server.models.song import Song
from openapi_server.models.extra_models import TokenModel  # noqa: F401
from openapi_server.security_api import get_token_BearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/artists/{id}/songs",
    responses={
        200: {"model": List[Song], "description": "Lista de canciones del artista."},
        404: {"description": "El artista especificado no existe."},
    },
    tags=["Canciones"],
    summary="Listar canciones de un artista",
    response_model_by_alias=True,
)
async def get_songs_by_artist(
    id: Annotated[str, Field(description="Identificador del artista cuyas canciones se consultan.")] = Path(..., description="Identificador del artista cuyas canciones se consultan.", examples=["art_12345"]),
) -> List[Song]:
    """Devuelve el repertorio de canciones vinculadas al artista, incluyendo sus identificadores de Spotify. """
    if not BaseCancionesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseCancionesApi.subclasses[0]().get_songs_by_artist(id)


@router.post(
    "/artists/{id}/songs",
    responses={
        201: {"model": Song, "description": "Canción creada y vinculada correctamente."},
        400: {"description": "Datos de la canción incorrectos."},
        401: {"description": "No autenticado."},
        403: {"description": "Acceso denegado."},
        404: {"description": "El artista especificado no existe."},
    },
    tags=["Canciones"],
    summary="Añadir una canción al repertorio de un artista",
    response_model_by_alias=True,
)
async def add_song_to_artist(
    id: Annotated[str, Field(description="Identificador del artista al que se añade la canción.")] = Path(..., description="Identificador del artista al que se añade la canción.", examples=["art_12345"]),
    create_song_request: Annotated[CreateSongRequest, Field(description="Información de la canción e identificadores externos.")] = Body(..., description="Información de la canción e identificadores externos."),
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    ),
) -> Song:
    """Asocia una nueva canción al artista especificado. """
    if not BaseCancionesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseCancionesApi.subclasses[0]().add_song_to_artist(id, create_song_request)
