# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from typing import Any, List
from typing_extensions import Annotated
from openapi_server.models.create_schedule_entry_request import CreateScheduleEntryRequest
from openapi_server.models.schedule_entry import ScheduleEntry
from openapi_server.security_api import get_token_BearerAuth

class BaseLineUpApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseLineUpApi.subclasses = BaseLineUpApi.subclasses + (cls,)
    async def get_event_lineup(
        self,
        id: Annotated[str, Field(description="Identificador del evento.")],
    ) -> List[ScheduleEntry]:
        """Devuelve las actuaciones programadas en los escenarios y sus franjas horarias. """
        ...


    async def add_schedule_entry(
        self,
        id: Annotated[str, Field(description="Identificador del evento al que se añade la actuación.")],
        create_schedule_entry_request: Annotated[CreateScheduleEntryRequest, Field(description="Datos del artista, escenario y horario.")],
    ) -> ScheduleEntry:
        """Registra la actuación de un artista en un escenario y franja horaria. Antes de crear la entrada, este microservicio realiza una COMUNICACIÓN SÍNCRONA de tipo CONSULTA: Gestión de Eventos -&gt; Catálogo Musical -&gt; GET /artists/{artistId} para validar que el artista existe en el catálogo musical. """
        ...
