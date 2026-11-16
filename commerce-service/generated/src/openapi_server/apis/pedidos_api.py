
import importlib
import pkgutil
from typing import List

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path
)
from fastapi.security import HTTPAuthorizationCredentials

from openapi_server.apis.pedidos_api_base import (
    BasePedidosApi
)
from openapi_server.models.order import Order
from openapi_server.models.order_request import OrderRequest
from openapi_server.models.update_order_status_request import (
    UpdateOrderStatusRequest
)
from openapi_server.security_api import (
    bearer_auth,
    obtener_usuario_actual,
    obtener_administrador,
    validar_comprador
)

import openapi_server.impl


router = APIRouter()

ns_pkg = openapi_server.impl

for _, name, _ in pkgutil.iter_modules(
    ns_pkg.__path__,
    ns_pkg.__name__ + "."
):
    importlib.import_module(name)


def obtener_implementacion():
    if not BasePedidosApi.subclasses:
        raise HTTPException(
            status_code=500,
            detail="API de Pedidos no implementada"
        )

    return BasePedidosApi.subclasses[0]()


# ============================================================
# POST /orders
# ============================================================

@router.post(
    "/orders",
    tags=["Pedidos"],
    summary="Crear un nuevo pedido",
    status_code=201,
    response_model=Order,
    responses={
        400: {"description": "Datos incorrectos"},
        401: {"description": "No autenticado"},
        403: {"description": "Comprador no autorizado"},
        404: {"description": "Usuario no encontrado"},
        409: {"description": "Stock insuficiente"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def create_order(
    order_request: OrderRequest = Body(...),
    usuario_actual: dict = Depends(obtener_usuario_actual),
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_auth
    )
) -> Order:

    # Impedir compras con el identificador de otro usuario.
    if usuario_actual["id"] != order_request.user_id:
        raise HTTPException(
            status_code=403,
            detail="No puedes comprar en nombre de otro usuario"
        )

    # Consulta sincronica a GET /users/{userId}
    # requerida por el contrato OpenAPI.
    await validar_comprador(
        order_request.user_id,
        credentials
    )

    return await obtener_implementacion().create_order(
        order_request,
        usuario_actual
    )


# ============================================================
# GET /orders/user/{userId}
# ============================================================

@router.get(
    "/orders/user/{userId}",
    tags=["Pedidos"],
    summary="Consultar historial de pedidos",
    response_model=List[Order],
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "No autorizado"}
    }
)
async def get_orders_by_user(
    userId: str = Path(...),
    usuario_actual: dict = Depends(obtener_usuario_actual)
) -> List[Order]:

    return await obtener_implementacion().get_orders_by_user(
        userId,
        usuario_actual
    )


# ============================================================
# GET /orders/{id}
# ============================================================

@router.get(
    "/orders/{id}",
    tags=["Pedidos"],
    summary="Consultar detalle de un pedido",
    response_model=Order,
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "No autorizado"},
        404: {"description": "Pedido no encontrado"}
    }
)
async def get_order_by_id(
    id: str = Path(...),
    usuario_actual: dict = Depends(obtener_usuario_actual)
) -> Order:

    return await obtener_implementacion().get_order_by_id(
        id,
        usuario_actual
    )


# ============================================================
# PUT /orders/{id}/status
# ============================================================

@router.put(
    "/orders/{id}/status",
    tags=["Pedidos"],
    summary="Actualizar estado de un pedido",
    status_code=200,
    responses={
        400: {"description": "Estado incorrecto"},
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        404: {"description": "Pedido no encontrado"},
        409: {"description": "Transicion de estado no permitida"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def update_order_status(
    id: str = Path(...),
    update_order_status_request: UpdateOrderStatusRequest = Body(...),
    usuario_actual: dict = Depends(obtener_administrador)
) -> None:

    return await obtener_implementacion().update_order_status(
        id,
        update_order_status_request,
        usuario_actual
    )


# ============================================================
# POST /orders/{id}/cancel
# ============================================================

@router.post(
    "/orders/{id}/cancel",
    tags=["Pedidos"],
    summary="Cancelar un pedido propio pendiente",
    status_code=200,
    responses={
        200: {
            "description": "Pedido cancelado correctamente"
        },
        401: {
            "description": "No autenticado"
        },
        403: {
            "description": "El pedido pertenece a otro usuario"
        },
        404: {
            "description": "Pedido no encontrado"
        },
        409: {
            "description": "El pedido ya no puede cancelarse"
        },
        503: {
            "description": "Autenticacion no disponible"
        }
    }
)
async def cancel_order(
    id: str = Path(...),
    usuario_actual: dict = Depends(obtener_usuario_actual)
) -> None:

    return await obtener_implementacion().cancel_order(
        id,
        usuario_actual
    )
