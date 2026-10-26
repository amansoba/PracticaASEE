# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from typing import Any, List, Optional
from typing_extensions import Annotated
from openapi_server.models.create_product_request import CreateProductRequest
from openapi_server.models.product import Product
from openapi_server.security_api import get_token_BearerAuth

class BaseProductosApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseProductosApi.subclasses = BaseProductosApi.subclasses + (cls,)
    async def get_products(
        self,
        category: Annotated[Optional[str], Field(description="Filtra productos por categoría (ej. ropa, accesorios).")],
    ) -> List[Product]:
        """Devuelve el catálogo de merchandising disponible para compra. Permite filtrado por categoría. """
        ...


    async def create_product(
        self,
        create_product_request: Annotated[CreateProductRequest, Field(description="Datos del producto y desglose de inventario.")],
    ) -> Product:
        """Añade un nuevo artículo al catálogo con sus tallas y stock inicial. Operación exclusiva para administradores. """
        ...


    async def get_product_by_id(
        self,
        id: Annotated[str, Field(description="Identificador único del producto en el catálogo.")],
    ) -> Product:
        """Devuelve la ficha detallada de un producto de la tienda y su stock por talla. """
        ...


    async def update_product(
        self,
        id: Annotated[str, Field(description="Identificador del producto a modificar.")],
        create_product_request: Annotated[CreateProductRequest, Field(description="Campos a modificar del producto.")],
    ) -> Product:
        """Actualiza precio, imágenes o stock disponible de un artículo. Exclusivo para administradores. """
        ...


    async def delete_product(
        self,
        id: Annotated[str, Field(description="Identificador del producto a retirar.")],
    ) -> None:
        """Elimina un artículo de la tienda oficial. Operación exclusiva para administradores. """
        ...
