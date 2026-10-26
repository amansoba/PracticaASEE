
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select

from openapi_server.apis.artistas_api_base import BaseArtistasApi
from openapi_server.models.artist import Artist
from openapi_server.models.create_artist_request import (
    CreateArtistRequest
)

from openapi_server.database import SessionLocal
from openapi_server.db_models import ArtistDB


def convertir_artista(artista: ArtistDB) -> Artist:
    return Artist(
        id=artista.id,
        name=artista.name,
        genre=artista.genre,
        biography=artista.biography,
        image_url=artista.image_url
    )


def datos_artista(solicitud: CreateArtistRequest) -> dict:
    nombre = solicitud.name.strip()
    genero = solicitud.genre.strip()

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre del artista es obligatorio"
        )

    if not genero:
        raise HTTPException(
            status_code=400,
            detail="El genero musical es obligatorio"
        )

    return {
        "name": nombre,
        "genre": genero,
        "biography": solicitud.biography,
        "image_url": (
            str(solicitud.image_url)
            if solicitud.image_url is not None
            else None
        )
    }


class ArtistasApiImpl(BaseArtistasApi):

    # GET /artists
    async def get_artists(
        self,
        genre: str | None,
        search: str | None
    ) -> list[Artist]:

        with SessionLocal() as db:
            consulta = select(ArtistDB)

            if genre and genre.strip():
                consulta = consulta.where(
                    ArtistDB.genre.ilike(
                        f"%{genre.strip()}%"
                    )
                )

            if search and search.strip():
                consulta = consulta.where(
                    ArtistDB.name.ilike(
                        f"%{search.strip()}%"
                    )
                )

            consulta = consulta.order_by(
                ArtistDB.name,
                ArtistDB.id
            )

            artistas = db.scalars(consulta).all()

            return [
                convertir_artista(artista)
                for artista in artistas
            ]

    # POST /artists
    async def create_artist(
        self,
        create_artist_request: CreateArtistRequest
    ) -> Artist:

        datos = datos_artista(create_artist_request)

        with SessionLocal() as db:
            nuevo_artista = ArtistDB(
                id=f"art_{uuid4().hex}",
                **datos
            )

            db.add(nuevo_artista)
            db.commit()
            db.refresh(nuevo_artista)

            return convertir_artista(nuevo_artista)

    # GET /artists/{id}
    async def get_artist_by_id(
        self,
        id: str
    ) -> Artist:

        with SessionLocal() as db:
            artista = db.get(ArtistDB, id)

            if artista is None:
                raise HTTPException(
                    status_code=404,
                    detail="Artista no encontrado"
                )

            return convertir_artista(artista)

    # PUT /artists/{id}
    async def update_artist(
        self,
        id: str,
        create_artist_request: CreateArtistRequest
    ) -> Artist:

        datos = datos_artista(create_artist_request)

        with SessionLocal() as db:
            artista = db.get(ArtistDB, id)

            if artista is None:
                raise HTTPException(
                    status_code=404,
                    detail="Artista no encontrado"
                )

            artista.name = datos["name"]
            artista.genre = datos["genre"]
            artista.biography = datos["biography"]
            artista.image_url = datos["image_url"]

            db.commit()
            db.refresh(artista)

            return convertir_artista(artista)

    # DELETE /artists/{id}
    async def delete_artist(
        self,
        id: str
    ) -> None:

        with SessionLocal() as db:
            artista = db.get(ArtistDB, id)

            if artista is None:
                raise HTTPException(
                    status_code=404,
                    detail="Artista no encontrado"
                )

            # La relacion SQLAlchemy elimina tambien
            # las canciones asociadas al artista.
            db.delete(artista)
            db.commit()

        return None
