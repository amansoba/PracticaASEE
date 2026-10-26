# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from typing import Any, List, Optional
from typing_extensions import Annotated
from openapi_server.models.artist import Artist
from openapi_server.models.create_artist_request import CreateArtistRequest
from openapi_server.security_api import get_token_BearerAuth

class BaseArtistasApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseArtistasApi.subclasses = BaseArtistasApi.subclasses + (cls,)
    async def get_artists(
        self,
        genre: Annotated[Optional[str], Field(description="Filtrar artistas por género musical.")],
        search: Annotated[Optional[str], Field(description="Búsqueda por texto libre en el nombre del artista.")],
    ) -> List[Artist]:
        """Devuelve el catálogo de artistas con filtros opcionales de búsqueda y género musical. No requiere comunicación con otros microservicios. """
        ...


    async def create_artist(
        self,
        create_artist_request: Annotated[CreateArtistRequest, Field(description="Información requerida para dar de alta al artista.")],
    ) -> Artist:
        """Registra un nuevo artista en el catálogo del festival. Operación restringida a administradores. """
        ...


    async def get_artist_by_id(
        self,
        id: Annotated[str, Field(description="Identificador único del artista.")],
    ) -> Artist:
        """Devuelve la información de un artista a partir de su identificador. Esta operación es consultada de forma síncrona por el microservicio de Gestión de Eventos. """
        ...


    async def update_artist(
        self,
        id: Annotated[str, Field(description="Identificador del artista que se actualizará.")],
        create_artist_request: Annotated[CreateArtistRequest, Field(description="Nuevos datos del artista.")],
    ) -> Artist:
        """Modifica la biografía, género o imagen de un artista. Operación para administradores. """
        ...


    async def delete_artist(
        self,
        id: Annotated[str, Field(description="Identificador del artista a eliminar.")],
    ) -> None:
        """Borra un artista del catálogo. Operación exclusiva para administradores. """
        ...
