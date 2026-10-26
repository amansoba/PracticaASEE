
import importlib
import pkgutil
from typing import List, Optional

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    Query
)

from openapi_server.apis.productos_api_base import (
    BaseProductosApi
)
from openapi_server.models.create_product_request import (
    CreateProductRequest
)
from openapi_server.models.product import Product
from openapi_server.security_api import obtener_administrador

import openapi_server.impl


router = APIRouter()

# Cargar las implementaciones generadas
ns_pkg = openapi_server.impl

for _, name, _ in pkgutil.iter_modules(
    ns_pkg.__path__,
    ns_pkg.__name__ + "."
):
    importlib.import_module(name)


def obtener_implementacion():
    if not BaseProductosApi.subclasses:
        raise HTTPException(
            status_code=500,
            detail="API de Productos no implementada"
        )

    return BaseProductosApi.subclasses[0]()


# ============================================================
# GET /products
# ============================================================

@router.get(
    "/products",
    tags=["Productos"],
    summary="Listar productos",
    response_model=List[Product]
)
async def get_products(
    category: Optional[str] = Query(
        default=None,
        description="Filtrar por categoria"
    )
) -> List[Product]:

    return await obtener_implementacion().get_products(
        category
    )


# ============================================================
# POST /products
# ============================================================

@router.post(
    "/products",
    tags=["Productos"],
    summary="Crear producto",
    status_code=201,
    response_model=Product,
    responses={
        400: {"description": "Datos invalidos"},
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def create_product(
    create_product_request: CreateProductRequest = Body(...),
    usuario_actual: dict = Depends(obtener_administrador)
) -> Product:

    return await obtener_implementacion().create_product(
        create_product_request
    )


# ============================================================
# GET /products/{id}
# ============================================================

@router.get(
    "/products/{id}",
    tags=["Productos"],
    summary="Consultar producto",
    response_model=Product,
    responses={
        404: {"description": "Producto no encontrado"}
    }
)
async def get_product_by_id(
    id: str = Path(...)
) -> Product:

    return await obtener_implementacion().get_product_by_id(
        id
    )


# ============================================================
# PUT /products/{id}
# ============================================================

@router.put(
    "/products/{id}",
    tags=["Productos"],
    summary="Actualizar producto",
    response_model=Product,
    responses={
        400: {"description": "Datos invalidos"},
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        404: {"description": "Producto no encontrado"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def update_product(
    id: str = Path(...),
    create_product_request: CreateProductRequest = Body(...),
    usuario_actual: dict = Depends(obtener_administrador)
) -> Product:

    return await obtener_implementacion().update_product(
        id,
        create_product_request
    )


# ============================================================
# DELETE /products/{id}
# ============================================================

@router.delete(
    "/products/{id}",
    tags=["Productos"],
    summary="Eliminar producto",
    status_code=204,
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        404: {"description": "Producto no encontrado"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def delete_product(
    id: str = Path(...),
    usuario_actual: dict = Depends(obtener_administrador)
) -> None:

    await obtener_implementacion().delete_product(id)

    return None
