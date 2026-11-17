
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from openapi_server.database import SessionLocal
from openapi_server.db_models import OrderDB
from openapi_server.models.order import Order
from openapi_server.security_api import obtener_administrador
from openapi_server.impl.pedidos_impl import convertir_pedido


router = APIRouter()


@router.get(
    "/orders",
    tags=["Pedidos"],
    summary="Consultar todos los pedidos como administrador",
    response_model=list[Order],
    responses={
        200: {"description": "Listado global de pedidos"},
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def listar_todos_los_pedidos(
    usuario_actual: dict = Depends(obtener_administrador)
) -> list[Order]:

    with SessionLocal() as db:
        pedidos = db.scalars(
            select(OrderDB)
            .options(selectinload(OrderDB.items))
            .order_by(
                OrderDB.created_at.desc(),
                OrderDB.id
            )
        ).all()

        return [
            convertir_pedido(pedido)
            for pedido in pedidos
        ]
