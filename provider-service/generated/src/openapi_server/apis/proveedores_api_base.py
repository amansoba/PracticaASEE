# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from typing import Any, List
from typing_extensions import Annotated
from openapi_server.models.create_provider_request import CreateProviderRequest
from openapi_server.models.provider_profile import ProviderProfile
from openapi_server.security_api import get_token_BearerAuth

class BaseProveedoresApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseProveedoresApi.subclasses = BaseProveedoresApi.subclasses + (cls,)
    async def get_providers(
        self,
    ) -> List[ProviderProfile]:
        """Devuelve el listado de empresas proveedoras colaboradoras. Operación para administradores. """
        ...


    async def create_provider(
        self,
        create_provider_request: Annotated[CreateProviderRequest, Field(description="Datos fiscales y de contacto de la empresa.")],
    ) -> ProviderProfile:
        """Crea la ficha de empresa de un proveedor. Antes de registrar al proveedor, este microservicio realiza una COMUNICACIÓN SÍNCRONA de tipo CONSULTA: Gestión de Proveedores -&gt; Autenticación y Cuentas -&gt; GET /users/{userId} para verificar que el usuario existe y posee el rol &#39;provider&#39;. """
        ...


    async def get_provider_by_id(
        self,
        id: Annotated[str, Field(description="Identificador único del proveedor.")],
    ) -> ProviderProfile:
        """Devuelve la ficha con datos de contacto, fiscales y servicios de una empresa proveedora. """
        ...
