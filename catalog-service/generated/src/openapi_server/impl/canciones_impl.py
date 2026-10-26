
import os
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select

from openapi_server.apis.canciones_api_base import (
    BaseCancionesApi
)
from openapi_server.models.create_song_request import (
    CreateSongRequest
)
from openapi_server.models.song import Song

from openapi_server.database import SessionLocal
from openapi_server.db_models import ArtistDB, SongDB
from openapi_server.spotify_client import obtener_cancion_spotify


def convertir_cancion(cancion: SongDB) -> Song:
    return Song(
        id=cancion.id,
        artist_id=cancion.artist_id,
        title=cancion.title,
        spotify_id=cancion.spotify_id,
        spotify_url=cancion.spotify_url,
        preview_url=cancion.preview_url
    )


def spotify_configurado() -> bool:
    return bool(
        os.getenv("SPOTIFY_CLIENT_ID")
        and os.getenv("SPOTIFY_CLIENT_SECRET")
    )


class CancionesApiImpl(BaseCancionesApi):

    # GET /artists/{id}/songs
    async def get_songs_by_artist(
        self,
        id: str
    ) -> list[Song]:

        with SessionLocal() as db:
            artista = db.get(ArtistDB, id)

            if artista is None:
                raise HTTPException(
                    status_code=404,
                    detail="Artista no encontrado"
                )

            canciones = db.scalars(
                select(SongDB)
                .where(SongDB.artist_id == id)
                .order_by(SongDB.title, SongDB.id)
            ).all()

            return [
                convertir_cancion(cancion)
                for cancion in canciones
            ]

    # POST /artists/{id}/songs
    async def add_song_to_artist(
        self,
        id: str,
        create_song_request: CreateSongRequest
    ) -> Song:

        titulo = create_song_request.title.strip()

        if not titulo:
            raise HTTPException(
                status_code=400,
                detail="El titulo de la cancion es obligatorio"
            )

        spotify_id = create_song_request.spotify_id

        if spotify_id is not None:
            spotify_id = spotify_id.strip() or None

        spotify_url = (
            str(create_song_request.spotify_url)
            if create_song_request.spotify_url is not None
            else None
        )

        preview_url = (
            str(create_song_request.preview_url)
            if create_song_request.preview_url is not None
            else None
        )

        # Comprobar primero que el artista existe.
        with SessionLocal() as db:
            artista = db.get(ArtistDB, id)

            if artista is None:
                raise HTTPException(
                    status_code=404,
                    detail="Artista no encontrado"
                )

        # Consultar Spotify solamente cuando:
        # - Se ha enviado un spotify_id
        # - Tenemos credenciales configuradas
        if spotify_id and spotify_configurado():

            datos_spotify = await obtener_cancion_spotify(
                spotify_id
            )

            if not datos_spotify.get("spotify_id"):
                raise HTTPException(
                    status_code=503,
                    detail="Spotify no devolvio un ID valido"
                )

            # Priorizar los metadatos verificados de Spotify.
            spotify_id = datos_spotify["spotify_id"]

            if datos_spotify.get("title"):
                titulo = datos_spotify["title"]

            spotify_url = datos_spotify.get("spotify_url")
            preview_url = datos_spotify.get("preview_url")

        # Guardar la cancion en PostgreSQL.
        with SessionLocal() as db:
            artista = db.get(ArtistDB, id)

            if artista is None:
                raise HTTPException(
                    status_code=404,
                    detail="Artista no encontrado"
                )

            nueva_cancion = SongDB(
                id=f"song_{uuid4().hex}",
                artist_id=artista.id,
                title=titulo,
                spotify_id=spotify_id,
                spotify_url=spotify_url,
                preview_url=preview_url
            )

            db.add(nueva_cancion)
            db.commit()
            db.refresh(nueva_cancion)

            return convertir_cancion(nueva_cancion)
