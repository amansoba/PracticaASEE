
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from openapi_server.apis.pedidos_api_base import BasePedidosApi
from openapi_server.models.order import Order
from openapi_server.models.order_item import OrderItem
from openapi_server.models.order_request import OrderRequest
from openapi_server.models.update_order_status_request import (
    UpdateOrderStatusRequest
)

from openapi_server.database import SessionLocal
from openapi_server.db_models import (
    OrderDB,
    OrderItemDB,
    ProductDB,
    ProductVariantDB
)


# ============================================================
# ESTADOS Y TRANSICIONES PERMITIDAS
# ============================================================

ESTADOS = {
    "pending",
    "paid",
    "preparing",
    "shipped",
    "delivered",
    "cancelled"
}

TRANSICIONES = {
    "pending": {"paid", "cancelled"},
    "paid": {"preparing"},
    "preparing": {"shipped"},
    "shipped": {"delivered"},
    "delivered": set(),
    "cancelled": set()
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def convertir_pedido(pedido: OrderDB) -> Order:
    return Order(
        id=pedido.id,
        user_id=pedido.user_id,
        items=[
            OrderItem(
                product_id=item.product_id,
                size=item.size,
                quantity=item.quantity,
                unit_price=float(item.unit_price)
            )
            for item in pedido.items
        ],
        total_price=float(pedido.total_price),
        status=pedido.status,
        created_at=pedido.created_at
    )


def obtener_pedido(db, pedido_id: str):
    return db.scalar(
        select(OrderDB)
        .options(selectinload(OrderDB.items))
        .where(OrderDB.id == pedido_id)
    )


def comprobar_usuario(
    usuario_actual: dict,
    usuario_id: str
):
    if usuario_actual["id"] != usuario_id:
        raise HTTPException(
            status_code=403,
            detail="No puedes operar en nombre de otro usuario"
        )


def comprobar_propietario_o_admin(
    usuario_actual: dict,
    usuario_id: str
):
    if (
        usuario_actual["id"] != usuario_id
        and usuario_actual["role"] != "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para consultar este pedido"
        )


def comprobar_admin(usuario_actual: dict):
    if usuario_actual["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Se requiere rol de administrador"
        )


def validar_articulos(items):
    if not items:
        raise HTTPException(
            status_code=400,
            detail="El pedido debe contener al menos un articulo"
        )

    cantidades = {}

    for item in items:
        producto_id = item.product_id.strip()
        talla = item.size.strip()

        if not producto_id or not talla:
            raise HTTPException(
                status_code=400,
                detail="Producto y talla son obligatorios"
            )

        if item.quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail="La cantidad debe ser positiva"
            )

        clave = (producto_id, talla)

        cantidades[clave] = (
            cantidades.get(clave, 0)
            + item.quantity
        )

    return cantidades


def devolver_stock(db, pedido: OrderDB):
    """
    Devuelve al inventario las unidades reservadas
    en un pedido que pasa de pending a cancelled.

    Se ejecuta dentro de la misma transaccion
    que actualiza el estado del pedido.
    """

    cantidades = {}

    for item in pedido.items:
        clave = (item.product_id, item.size)

        cantidades[clave] = (
            cantidades.get(clave, 0)
            + item.quantity
        )

    productos_ids = sorted({
        producto_id
        for producto_id, _ in cantidades
    })

    # Bloquear productos para coordinar esta operacion
    # con compras y actualizaciones de inventario.
    productos = db.scalars(
        select(ProductDB)
        .where(ProductDB.id.in_(productos_ids))
        .order_by(ProductDB.id)
        .with_for_update()
    ).all()

    if len(productos) != len(productos_ids):
        raise HTTPException(
            status_code=409,
            detail=(
                "No se puede reponer el inventario: "
                "hay productos eliminados"
            )
        )

    variantes = db.scalars(
        select(ProductVariantDB)
        .where(
            ProductVariantDB.product_id.in_(
                productos_ids
            )
        )
        .order_by(
            ProductVariantDB.product_id,
            ProductVariantDB.size
        )
        .with_for_update()
    ).all()

    variantes_por_clave = {
        (variante.product_id, variante.size): variante
        for variante in variantes
    }

    # Validar primero todas las tallas.
    for clave in cantidades:
        if clave not in variantes_por_clave:
            raise HTTPException(
                status_code=409,
                detail=(
                    "No se puede reponer el inventario: "
                    "hay tallas que ya no existen"
                )
            )

    # Reponer el inventario.
    for clave, cantidad in cantidades.items():
        variantes_por_clave[clave].stock += cantidad


# ============================================================
# IMPLEMENTACION DE PEDIDOS
# ============================================================

class PedidosApiImpl(BasePedidosApi):

    # POST /orders
    async def create_order(
        self,
        order_request: OrderRequest,
        usuario_actual: dict
    ) -> Order:

        comprobar_usuario(
            usuario_actual,
            order_request.user_id
        )

        direccion = order_request.shipping_address.strip()

        if not direccion:
            raise HTTPException(
                status_code=400,
                detail="La direccion de envio es obligatoria"
            )

        cantidades = validar_articulos(
            order_request.items
        )

        productos_ids = sorted({
            producto_id
            for producto_id, _ in cantidades
        })

        with SessionLocal() as db:
            try:
                productos = db.scalars(
                    select(ProductDB)
                    .where(ProductDB.id.in_(productos_ids))
                    .order_by(ProductDB.id)
                    .with_for_update()
                ).all()

                productos_por_id = {
                    producto.id: producto
                    for producto in productos
                }

                if len(productos_por_id) != len(productos_ids):
                    raise HTTPException(
                        status_code=400,
                        detail="Hay productos que no existen"
                    )

                variantes = db.scalars(
                    select(ProductVariantDB)
                    .where(
                        ProductVariantDB.product_id.in_(
                            productos_ids
                        )
                    )
                    .order_by(
                        ProductVariantDB.product_id,
                        ProductVariantDB.size
                    )
                    .with_for_update()
                ).all()

                variantes_por_clave = {
                    (variante.product_id, variante.size): variante
                    for variante in variantes
                }

                total = Decimal("0.00")
                articulos_pedido = []

                for clave, cantidad in sorted(cantidades.items()):
                    producto_id, talla = clave

                    variante = variantes_por_clave.get(clave)

                    if variante is None:
                        raise HTTPException(
                            status_code=400,
                            detail=(
                                "La talla seleccionada "
                                "no existe para el producto"
                            )
                        )

                    if variante.stock < cantidad:
                        raise HTTPException(
                            status_code=409,
                            detail=(
                                "Stock insuficiente para "
                                f"{producto_id}, talla {talla}"
                            )
                        )

                    producto = productos_por_id[producto_id]
                    precio_unitario = producto.price

                    total += precio_unitario * cantidad
                    variante.stock -= cantidad

                    articulos_pedido.append(
                        OrderItemDB(
                            product_id=producto_id,
                            size=talla,
                            quantity=cantidad,
                            unit_price=precio_unitario
                        )
                    )

                pedido = OrderDB(
                    id=f"ord_{uuid4().hex}",
                    user_id=order_request.user_id,
                    shipping_address=direccion,
                    payment_method_id=(
                        order_request.payment_method_id
                    ),
                    total_price=total,
                    status="pending",
                    items=articulos_pedido
                )

                db.add(pedido)
                db.commit()

                pedido = obtener_pedido(db, pedido.id)

                return convertir_pedido(pedido)

            except Exception:
                db.rollback()
                raise

    # GET /orders/user/{userId}
    async def get_orders_by_user(
        self,
        userId: str,
        usuario_actual: dict
    ) -> list[Order]:

        comprobar_propietario_o_admin(
            usuario_actual,
            userId
        )

        with SessionLocal() as db:
            pedidos = db.scalars(
                select(OrderDB)
                .options(selectinload(OrderDB.items))
                .where(OrderDB.user_id == userId)
                .order_by(
                    OrderDB.created_at.desc(),
                    OrderDB.id
                )
            ).all()

            return [
                convertir_pedido(pedido)
                for pedido in pedidos
            ]

    # GET /orders/{id}
    async def get_order_by_id(
        self,
        id: str,
        usuario_actual: dict
    ) -> Order:

        with SessionLocal() as db:
            pedido = obtener_pedido(db, id)

            if pedido is None:
                raise HTTPException(
                    status_code=404,
                    detail="Pedido no encontrado"
                )

            comprobar_propietario_o_admin(
                usuario_actual,
                pedido.user_id
            )

            return convertir_pedido(pedido)

    # PUT /orders/{id}/status
    async def update_order_status(
        self,
        id: str,
        update_order_status_request: UpdateOrderStatusRequest,
        usuario_actual: dict
    ) -> None:

        comprobar_admin(usuario_actual)

        nuevo_estado = update_order_status_request.status

        if hasattr(nuevo_estado, "value"):
            nuevo_estado = nuevo_estado.value

        if nuevo_estado not in ESTADOS:
            raise HTTPException(
                status_code=400,
                detail="Estado de pedido no permitido"
            )

        with SessionLocal() as db:
            try:
                pedido = db.scalar(
                    select(OrderDB)
                    .where(OrderDB.id == id)
                    .with_for_update()
                )

                if pedido is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Pedido no encontrado"
                    )

                estado_actual = pedido.status

                # Repetir el estado no debe modificar el stock.
                if nuevo_estado == estado_actual:
                    return None

                if nuevo_estado not in TRANSICIONES[estado_actual]:
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            "Transicion de estado no permitida: "
                            f"{estado_actual} -> {nuevo_estado}"
                        )
                    )

                if (
                    estado_actual == "pending"
                    and nuevo_estado == "cancelled"
                ):
                    # Cargar los articulos del pedido.
                    # La reposicion se hace en la misma
                    # transaccion que cambia el estado.
                    _ = pedido.items
                    devolver_stock(db, pedido)

                pedido.status = nuevo_estado

                db.commit()

                return None

            except Exception:
                db.rollback()
                raise

    # POST /orders/{id}/cancel
    async def cancel_order(
        self,
        id: str,
        usuario_actual: dict
    ) -> None:
        """
        Permite al propietario cancelar su pedido
        mientras permanezca pendiente.

        La cancelacion y la reposicion del stock
        se realizan en una unica transaccion.
        """

        with SessionLocal() as db:
            try:
                # Bloquear el pedido para impedir que dos
                # cancelaciones devuelvan el stock dos veces.
                pedido = db.scalar(
                    select(OrderDB)
                    .where(OrderDB.id == id)
                    .with_for_update()
                )

                if pedido is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Pedido no encontrado"
                    )

                # Comprobar la identidad antes de consultar
                # o modificar el estado del pedido.
                comprobar_usuario(
                    usuario_actual,
                    pedido.user_id
                )

                # Una cancelacion repetida no debe
                # reponer el inventario nuevamente.
                if pedido.status == "cancelled":
                    return None

                # Solo los pedidos pendientes se pueden
                # cancelar desde la cuenta del cliente.
                if pedido.status != "pending":
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            "Solo se pueden cancelar "
                            "pedidos pendientes"
                        )
                    )

                # Cargar los articulos y reponer stock
                # reutilizando la funcion ya existente.
                _ = pedido.items
                devolver_stock(db, pedido)

                # Actualizar el pedido dentro de la
                # misma transaccion de inventario.
                pedido.status = "cancelled"

                db.commit()

                return None

            except Exception:
                db.rollback()
                raise

    # POST /orders/{id}/pay
    async def pay_order(
        self,
        id: str,
        payment_token: str,
        usuario_actual: dict
    ) -> None:
        """
        Simula el pago de un pedido pendiente.

        No realiza ningun cobro real ni se conecta
        con una pasarela de pagos.
        """

        with SessionLocal() as db:
            try:
                # Bloquear el pedido para evitar que
                # dos pagos simultaneos lo procesen
                # dos veces o interfieran con su cancelacion.
                pedido = db.scalar(
                    select(OrderDB)
                    .where(OrderDB.id == id)
                    .with_for_update()
                )

                if pedido is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Pedido no encontrado"
                    )

                # Solo el propietario puede pagar.
                comprobar_usuario(
                    usuario_actual,
                    pedido.user_id
                )

                # Solo admitimos la transicion
                # pending -> paid.
                if pedido.status != "pending":
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            "Solo se pueden pagar "
                            "pedidos pendientes"
                        )
                    )

                # Token ficticio aceptado exclusivamente
                # en este entorno de simulacion.
                if payment_token != "tok_test_success":
                    raise HTTPException(
                        status_code=400,
                        detail="Pago simulado rechazado"
                    )

                # El stock ya se descuento cuando
                # se creo el pedido.
                # Aqui solo actualizamos su estado.
                pedido.status = "paid"

                db.commit()

                return None

            except Exception:
                db.rollback()
                raise
