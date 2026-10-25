
import importlib
import pkgutil
from typing import List, Optional

from fastapi import (
    APIRouter,
    Body,
    HTTPException,
    Path,
    Query,
    Security
)

from openapi_server.apis.artistas_api_base import (
    BaseArtistasApi
)
from openapi_server.models.artist import Artist
from openapi_server.models.create_artist_request import (
    CreateArtistRequest
)
from openapi_server.models.extra_models import TokenModel
from openapi_server.security_api import get_admin_BearerAuth

import openapi_server.impl


router = APIRouter()

# Cargar automaticamente las implementaciones
ns_pkg = openapi_server.impl

for _, name, _ in pkgutil.iter_modules(
    ns_pkg.__path__,
    ns_pkg.__name__ + "."
):
    importlib.import_module(name)


def obtener_implementacion():
    if not BaseArtistasApi.subclasses:
        raise HTTPException(
            status_code=500,
            detail="API de Artistas no implementada"
        )

    return BaseArtistasApi.subclasses[0]()


# GET /artists
@router.get(
    "/artists",
    tags=["Artistas"],
    summary="Consultar lista de artistas",
    response_model=List[Artist],
    responses={
        200: {
            "description": "Lista de artistas devuelta correctamente."
        }
    }
)
async def get_artists(
    genre: Optional[str] = Query(
        default=None,
        description="Filtrar por genero musical"
    ),
    search: Optional[str] = Query(
        default=None,
        description="Buscar por nombre"
    )
) -> List[Artist]:

    return await obtener_implementacion().get_artists(
        genre,
        search
    )


# POST /artists
@router.post(
    "/artists",
    tags=["Artistas"],
    summary="Crear un nuevo artista",
    status_code=201,
    response_model=Artist,
    responses={
        400: {"description": "Datos invalidos"},
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def create_artist(
    create_artist_request: CreateArtistRequest = Body(...),
    token_BearerAuth: TokenModel = Security(
        get_admin_BearerAuth
    )
) -> Artist:

    return await obtener_implementacion().create_artist(
        create_artist_request
    )


# GET /artists/{id}
@router.get(
    "/artists/{id}",
    tags=["Artistas"],
    summary="Obtener el detalle de un artista",
    response_model=Artist,
    responses={
        404: {"description": "Artista no encontrado"}
    }
)
async def get_artist_by_id(
    id: str = Path(...)
) -> Artist:

    return await obtener_implementacion().get_artist_by_id(
        id
    )


# PUT /artists/{id}
@router.put(
    "/artists/{id}",
    tags=["Artistas"],
    summary="Actualizar ficha de un artista",
    response_model=Artist,
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        404: {"description": "Artista no encontrado"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def update_artist(
    id: str = Path(...),
    create_artist_request: CreateArtistRequest = Body(...),
    token_BearerAuth: TokenModel = Security(
        get_admin_BearerAuth
    )
) -> Artist:

    return await obtener_implementacion().update_artist(
        id,
        create_artist_request
    )


# DELETE /artists/{id}
@router.delete(
    "/artists/{id}",
    tags=["Artistas"],
    summary="Eliminar un artista",
    status_code=204,
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        404: {"description": "Artista no encontrado"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def delete_artist(
    id: str = Path(...),
    token_BearerAuth: TokenModel = Security(
        get_admin_BearerAuth
    )
) -> None:

    await obtener_implementacion().delete_artist(id)

    return None
