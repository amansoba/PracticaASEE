# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.artistas_api_base import BaseArtistasApi
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
from typing import Any, List, Optional
from typing_extensions import Annotated
from openapi_server.models.artist import Artist
from openapi_server.models.create_artist_request import CreateArtistRequest
from openapi_server.models.extra_models import TokenModel  # noqa: F401
from openapi_server.security_api import get_token_BearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/artists",
    responses={
        200: {"model": List[Artist], "description": "Lista de artistas devuelta correctamente."},
    },
    tags=["Artistas"],
    summary="Consultar lista de artistas",
    response_model_by_alias=True,
)
async def get_artists(
    genre: Annotated[Optional[str], Field(description="Filtrar artistas por género musical.")] = Query(None, description="Filtrar artistas por género musical.", alias="genre", examples=["Electrónica"]),
    search: Annotated[Optional[str], Field(description="Búsqueda por texto libre en el nombre del artista.")] = Query(None, description="Búsqueda por texto libre en el nombre del artista.", alias="search", examples=["Daft"]),
) -> List[Artist]:
    """Devuelve el catálogo de artistas con filtros opcionales de búsqueda y género musical. No requiere comunicación con otros microservicios. """
    if not BaseArtistasApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseArtistasApi.subclasses[0]().get_artists(genre, search)


@router.post(
    "/artists",
    responses={
        201: {"model": Artist, "description": "Artista creado exitosamente."},
        400: {"description": "Datos del artista incompletos o inválidos."},
        401: {"description": "No autenticado."},
        403: {"description": "Acceso denegado. Requiere rol de administrador."},
    },
    tags=["Artistas"],
    summary="Crear un nuevo artista",
    response_model_by_alias=True,
)
async def create_artist(
    create_artist_request: Annotated[CreateArtistRequest, Field(description="Información requerida para dar de alta al artista.")] = Body(..., description="Información requerida para dar de alta al artista."),
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    ),
) -> Artist:
    """Registra un nuevo artista en el catálogo del festival. Operación restringida a administradores. """
    if not BaseArtistasApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseArtistasApi.subclasses[0]().create_artist(create_artist_request)


@router.get(
    "/artists/{id}",
    responses={
        200: {"model": Artist, "description": "Artista encontrado."},
        404: {"description": "No existe ningún artista con el identificador proporcionado."},
    },
    tags=["Artistas"],
    summary="Obtener el detalle de un artista",
    response_model_by_alias=True,
)
async def get_artist_by_id(
    id: Annotated[str, Field(description="Identificador único del artista.")] = Path(..., description="Identificador único del artista.", examples=["art_12345"]),
) -> Artist:
    """Devuelve la información de un artista a partir de su identificador. Esta operación es consultada de forma síncrona por el microservicio de Gestión de Eventos. """
    if not BaseArtistasApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseArtistasApi.subclasses[0]().get_artist_by_id(id)


@router.put(
    "/artists/{id}",
    responses={
        200: {"model": Artist, "description": "Artista actualizado correctamente."},
        401: {"description": "No autenticado."},
        403: {"description": "Acceso denegado."},
        404: {"description": "El artista indicado no existe."},
    },
    tags=["Artistas"],
    summary="Actualizar ficha de un artista",
    response_model_by_alias=True,
)
async def update_artist(
    id: Annotated[str, Field(description="Identificador del artista que se actualizará.")] = Path(..., description="Identificador del artista que se actualizará.", examples=["art_12345"]),
    create_artist_request: Annotated[CreateArtistRequest, Field(description="Nuevos datos del artista.")] = Body(..., description="Nuevos datos del artista."),
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    ),
) -> Artist:
    """Modifica la biografía, género o imagen de un artista. Operación para administradores. """
    if not BaseArtistasApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseArtistasApi.subclasses[0]().update_artist(id, create_artist_request)


@router.delete(
    "/artists/{id}",
    responses={
        204: {"description": "Artista eliminado satisfactoriamente."},
        401: {"description": "No autenticado."},
        403: {"description": "Acceso denegado."},
        404: {"description": "El artista no existe."},
    },
    tags=["Artistas"],
    summary="Eliminar un artista del catálogo",
    response_model_by_alias=True,
)
async def delete_artist(
    id: Annotated[str, Field(description="Identificador del artista a eliminar.")] = Path(..., description="Identificador del artista a eliminar.", examples=["art_12345"]),
    token_BearerAuth: TokenModel = Security(
        get_token_BearerAuth
    ),
) -> None:
    """Borra un artista del catálogo. Operación exclusiva para administradores. """
    if not BaseArtistasApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseArtistasApi.subclasses[0]().delete_artist(id)
