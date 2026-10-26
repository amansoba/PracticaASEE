# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from typing import Any, List
from typing_extensions import Annotated
from openapi_server.models.create_space_proposal_request import CreateSpaceProposalRequest
from openapi_server.models.space_proposal import SpaceProposal
from openapi_server.models.update_proposal_status_request import UpdateProposalStatusRequest
from openapi_server.security_api import get_token_BearerAuth

class BasePresupuestosYSolicitudesApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BasePresupuestosYSolicitudesApi.subclasses = BasePresupuestosYSolicitudesApi.subclasses + (cls,)
    async def create_space_proposal(
        self,
        create_space_proposal_request: Annotated[CreateSpaceProposalRequest, Field(description="Presupuesto propuesto y fechas de montaje.")],
    ) -> SpaceProposal:
        """El proveedor envía una cotización para cubrir un servicio o alquilar un espacio. Antes de crear la solicitud, este microservicio realiza dos COMUNICACIONES SÍNCRONAS de tipo CONSULTA: 1. Gestión de Proveedores -&gt; Autenticación y Cuentas -&gt; GET /users/{userId} (Valida permisos del proveedor). 2. Gestión de Proveedores -&gt; Gestión de Eventos -&gt; GET /events/{eventId} (Valida vigencia del festival). """
        ...


    async def get_proposals_by_provider(
        self,
        providerId: Annotated[str, Field(description="Identificador del proveedor.")],
    ) -> List[SpaceProposal]:
        """Devuelve el histórico de presupuestos presentados por una empresa colaboradora. """
        ...


    async def get_proposals_by_event(
        self,
        eventId: Annotated[str, Field(description="Identificador del evento consultado (referencia a Gestión de Eventos). ")],
    ) -> List[SpaceProposal]:
        """Devuelve los presupuestos recibidos para un evento concreto. Operación para administradores. """
        ...


    async def update_proposal_status(
        self,
        id: Annotated[str, Field(description="Identificador de la propuesta de presupuesto.")],
        update_proposal_status_request: Annotated[UpdateProposalStatusRequest, Field(description="Resolución de la propuesta.")],
    ) -> None:
        """Actualiza el estado de la propuesta (approved / rejected) y asigna formalmente al proveedor para el evento. Operación reservada para administradores. """
        ...
