
from fastapi import (
    APIRouter,
    Body,
    HTTPException,
    Path,
    Security
)

from openapi_server.database import SessionLocal
from openapi_server.db_models import ArtistDB, SongDB
from openapi_server.models.create_song_request import (
    CreateSongRequest
)
from openapi_server.models.song import Song
from openapi_server.models.extra_models import TokenModel
from openapi_server.security_api import get_admin_BearerAuth
from openapi_server.impl.canciones_impl import convertir_cancion


router = APIRouter()


def buscar_cancion(db, artist_id: str, song_id: str):
    artista = db.get(ArtistDB, artist_id)

    if artista is None:
        raise HTTPException(
            status_code=404,
            detail="Artista no encontrado"
        )

    cancion = db.get(SongDB, song_id)

    if cancion is None or cancion.artist_id != artist_id:
        raise HTTPException(
            status_code=404,
            detail="Cancion no encontrada"
        )

    return cancion


# ============================================================
# PUT - ACTUALIZAR CANCION
# ============================================================

@router.put(
    "/artists/{artistId}/songs/{songId}",
    tags=["Canciones"],
    summary="Actualizar una cancion",
    response_model=Song,
    responses={
        400: {"description": "Datos invalidos"},
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        404: {"description": "Artista o cancion no encontrados"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def actualizar_cancion(
    artistId: str = Path(...),
    songId: str = Path(...),
    solicitud: CreateSongRequest = Body(...),
    usuario: TokenModel = Security(get_admin_BearerAuth)
) -> Song:

    titulo = solicitud.title.strip()

    if not titulo:
        raise HTTPException(
            status_code=400,
            detail="El titulo de la cancion es obligatorio"
        )

    with SessionLocal() as db:
        cancion = buscar_cancion(
            db,
            artistId,
            songId
        )

        cancion.title = titulo
        cancion.spotify_id = (
            solicitud.spotify_id.strip() or None
            if solicitud.spotify_id is not None
            else None
        )
        cancion.spotify_url = (
            str(solicitud.spotify_url)
            if solicitud.spotify_url is not None
            else None
        )
        cancion.preview_url = (
            str(solicitud.preview_url)
            if solicitud.preview_url is not None
            else None
        )

        db.commit()
        db.refresh(cancion)

        return convertir_cancion(cancion)


# ============================================================
# DELETE - ELIMINAR CANCION
# ============================================================

@router.delete(
    "/artists/{artistId}/songs/{songId}",
    tags=["Canciones"],
    summary="Eliminar una cancion",
    status_code=204,
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        404: {"description": "Artista o cancion no encontrados"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def eliminar_cancion(
    artistId: str = Path(...),
    songId: str = Path(...),
    usuario: TokenModel = Security(get_admin_BearerAuth)
) -> None:

    with SessionLocal() as db:
        cancion = buscar_cancion(
            db,
            artistId,
            songId
        )

        db.delete(cancion)
        db.commit()

    return None
