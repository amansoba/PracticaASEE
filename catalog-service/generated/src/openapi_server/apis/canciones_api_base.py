# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from typing import Any, List
from typing_extensions import Annotated
from openapi_server.models.create_song_request import CreateSongRequest
from openapi_server.models.song import Song
from openapi_server.security_api import get_token_BearerAuth

class BaseCancionesApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseCancionesApi.subclasses = BaseCancionesApi.subclasses + (cls,)
    async def get_songs_by_artist(
        self,
        id: Annotated[str, Field(description="Identificador del artista cuyas canciones se consultan.")],
    ) -> List[Song]:
        """Devuelve el repertorio de canciones vinculadas al artista, incluyendo sus identificadores de Spotify. """
        ...


    async def add_song_to_artist(
        self,
        id: Annotated[str, Field(description="Identificador del artista al que se añade la canción.")],
        create_song_request: Annotated[CreateSongRequest, Field(description="Información de la canción e identificadores externos.")],
    ) -> Song:
        """Asocia una nueva canción al artista especificado. """
        ...
