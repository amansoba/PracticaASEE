# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from typing import Any, List
from typing_extensions import Annotated
from openapi_server.models.create_event_request import CreateEventRequest
from openapi_server.models.event import Event
from openapi_server.security_api import get_token_BearerAuth

class BaseEventosApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseEventosApi.subclasses = BaseEventosApi.subclasses + (cls,)
    async def get_all_events(
        self,
    ) -> List[Event]:
        """Devuelve la lista general de eventos y ediciones de festivales configurados. """
        ...


    async def create_event(
        self,
        create_event_request: Annotated[CreateEventRequest, Field(description="Información básica del evento.")],
    ) -> Event:
        """Da de alta un festival indicando nombre, fechas y recinto. Operación restringida a administradores. """
        ...


    async def get_event_by_id(
        self,
        id: Annotated[str, Field(description="Identificador único del evento.")],
    ) -> Event:
        """Devuelve las fechas, recinto y ubicación de un festival. Endpoint consultado de forma síncrona por Gestión de Proveedores para asociar espacios y servicios. """
        ...


    async def update_event(
        self,
        id: Annotated[str, Field(description="Identificador del evento a actualizar.")],
        create_event_request: Annotated[CreateEventRequest, Field(description="Nuevos datos del evento.")],
    ) -> Event:
        """Permite actualizar fechas o recintos de un evento existente. Operación para administradores. """
        ...


    async def delete_event(
        self,
        id: Annotated[str, Field(description="Identificador del evento a cancelar.")],
    ) -> None:
        """Elimina un festival del sistema. Operación para administradores. """
        ...
