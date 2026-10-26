# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from typing import Any, List
from typing_extensions import Annotated
from openapi_server.models.create_pass_config_request import CreatePassConfigRequest
from openapi_server.models.pass_config import PassConfig
from openapi_server.models.ticket import Ticket
from openapi_server.models.ticket_purchase_request import TicketPurchaseRequest
from openapi_server.security_api import get_token_BearerAuth

class BasePasesYEntradasApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BasePasesYEntradasApi.subclasses = BasePasesYEntradasApi.subclasses + (cls,)
    async def get_pass_configs_by_event(
        self,
        id: Annotated[str, Field(description="Identificador del evento.")],
    ) -> List[PassConfig]:
        """Devuelve los tipos de entrada disponibles para el evento (general, VIP, abono). """
        ...


    async def create_pass_config(
        self,
        id: Annotated[str, Field(description="Identificador del evento al que se asigna la entrada.")],
        create_pass_config_request: Annotated[CreatePassConfigRequest, Field(description="Configuración del pase y aforo.")],
    ) -> PassConfig:
        """Define precio, aforo máximo y beneficios de una modalidad de entrada. Operación para administradores. """
        ...


    async def purchase_ticket(
        self,
        ticket_purchase_request: Annotated[TicketPurchaseRequest, Field(description="Identificadores del evento, tipo de pase, usuario y token de pago.")],
    ) -> Ticket:
        """Emite una entrada nominal y decrementa el aforo del pase. Antes de emitir la entrada, este microservicio realiza una COMUNICACIÓN SÍNCRONA de tipo CONSULTA: Gestión de Eventos -&gt; Autenticación y Cuentas -&gt; GET /users/{userId} para validar la identidad del comprador y asociar la entrada a su propietario. """
        ...


    async def get_tickets_by_user(
        self,
        userId: Annotated[str, Field(description="Identificador del usuario propietario de las entradas.")],
    ) -> List[Ticket]:
        """Devuelve el listado de entradas emitidas asociadas al identificador del comprador. """
        ...
