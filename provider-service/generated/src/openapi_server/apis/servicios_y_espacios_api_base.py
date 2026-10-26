# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from typing import Any, List
from typing_extensions import Annotated
from openapi_server.models.create_external_service_request import CreateExternalServiceRequest
from openapi_server.models.create_space_request import CreateSpaceRequest
from openapi_server.models.external_service import ExternalService
from openapi_server.models.space import Space
from openapi_server.security_api import get_token_BearerAuth

class BaseServiciosYEspaciosApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseServiciosYEspaciosApi.subclasses = BaseServiciosYEspaciosApi.subclasses + (cls,)
    async def get_external_services(
        self,
    ) -> List[ExternalService]:
        """Devuelve el catálogo de tipos de servicios requeridos (escenarios, sonido, barras, iluminación). """
        ...


    async def create_external_service(
        self,
        create_external_service_request: Annotated[CreateExternalServiceRequest, Field(description="Información del servicio.")],
    ) -> ExternalService:
        """Añade un nuevo tipo de servicio al catálogo. Operación exclusiva de administradores. """
        ...


    async def get_spaces_by_event(
        self,
        event_id: Annotated[str, Field(description="Identificador del evento al que corresponden los espacios. Referencia hacia el microservicio de Gestión de Eventos. ")],
    ) -> List[Space]:
        """Devuelve las zonas disponibles para proveedores en un festival específico. """
        ...


    async def create_space(
        self,
        create_space_request: Annotated[CreateSpaceRequest, Field(description="Información técnica y precio del espacio.")],
    ) -> Space:
        """Registra una zona alquilable en el recinto de un festival. Antes de registrar el espacio, este microservicio realiza una COMUNICACIÓN SÍNCRONA de tipo CONSULTA: Gestión de Proveedores -&gt; Gestión de Eventos -&gt; GET /events/{eventId} para validar que el evento existe y obtener su información de recinto. """
        ...
