# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from typing import Any, List
from typing_extensions import Annotated
from openapi_server.models.order import Order
from openapi_server.models.order_request import OrderRequest
from openapi_server.models.update_order_status_request import UpdateOrderStatusRequest
from openapi_server.security_api import get_token_BearerAuth

class BasePedidosApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BasePedidosApi.subclasses = BasePedidosApi.subclasses + (cls,)
    async def create_order(
        self,
        order_request: Annotated[OrderRequest, Field(description="Información de artículos, dirección de envío y referencia del comprador.")],
    ) -> Order:
        """Procesa la compra de los artículos enviados en el carrito y decrementa el stock disponible. Antes de crear el pedido, este microservicio realiza una COMUNICACIÓN SÍNCRONA de tipo CONSULTA: Tienda -&gt; Autenticación y Cuentas -&gt; GET /users/{userId} Esto valida que el usuario existe y está autorizado a operar. """
        ...


    async def get_orders_by_user(
        self,
        userId: Annotated[str, Field(description="Identificador del usuario propietario de los pedidos.")],
    ) -> List[Order]:
        """Devuelve el histórico de compras efectuadas por el cliente. """
        ...


    async def get_order_by_id(
        self,
        id: Annotated[str, Field(description="Identificador único del pedido.")],
    ) -> Order:
        """Devuelve la información completa de una orden de compra por su identificador. """
        ...


    async def update_order_status(
        self,
        id: Annotated[str, Field(description="Identificador del pedido que cambiará de estado.")],
        update_order_status_request: Annotated[UpdateOrderStatusRequest, Field(description="Nuevo estado logístico.")],
    ) -> None:
        """Modifica el estado del envío del paquete (paid, shipped, delivered, cancelled). Operación reservada para administradores del festival. """
        ...
