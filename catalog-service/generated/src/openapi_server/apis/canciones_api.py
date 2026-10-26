
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

from openapi_server.apis.canciones_api_base import (
    BaseCancionesApi
)
from openapi_server.models.create_song_request import (
    CreateSongRequest
)
from openapi_server.models.song import Song
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
    if not BaseCancionesApi.subclasses:
        raise HTTPException(
            status_code=500,
            detail="API de Canciones no implementada"
        )

    return BaseCancionesApi.subclasses[0]()


# GET /artists/{id}/songs
@router.get(
    "/artists/{id}/songs",
    tags=["Canciones"],
    summary="Listar canciones de un artista",
    response_model=List[Song],
    responses={
        404: {"description": "Artista no encontrado"}
    }
)
async def get_songs_by_artist(
    id: str = Path(...)
) -> List[Song]:

    return await obtener_implementacion().get_songs_by_artist(
        id
    )


# POST /artists/{id}/songs
@router.post(
    "/artists/{id}/songs",
    tags=["Canciones"],
    summary="Anadir una cancion a un artista",
    status_code=201,
    response_model=Song,
    responses={
        400: {"description": "Datos invalidos"},
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        404: {"description": "Artista no encontrado"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def add_song_to_artist(
    id: str = Path(...),
    create_song_request: CreateSongRequest = Body(...),
    token_BearerAuth: TokenModel = Security(
        get_admin_BearerAuth
    )
) -> Song:

    return await obtener_implementacion().add_song_to_artist(
        id,
        create_song_request
    )
