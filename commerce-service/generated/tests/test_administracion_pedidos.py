
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from openapi_server.main import app
from openapi_server.database import SessionLocal
from openapi_server.db_models import OrderDB, OrderItemDB
from openapi_server.security_api import obtener_usuario_actual


ADMIN = {
    "id": "usr_admin_test",
    "role": "admin"
}

CLIENTE = {
    "id": "usr_cliente_test",
    "role": "client"
}


def autenticar(usuario):
    app.dependency_overrides[
        obtener_usuario_actual
    ] = lambda: usuario


def crear_pedidos_prueba():

    momento = datetime.now(timezone.utc)

    with SessionLocal() as db:

        pedido_1 = OrderDB(
            id="ord_admin_001",
            user_id="usr_cliente_001",
            shipping_address="Calle Uno 1",
            payment_method_id="pm_test",
            total_price=Decimal("25.00"),
            status="pending",
            created_at=momento - timedelta(minutes=5),
            items=[
                OrderItemDB(
                    product_id="prod_001",
                    size="M",
                    quantity=1,
                    unit_price=Decimal("25.00")
                )
            ]
        )

        pedido_2 = OrderDB(
            id="ord_admin_002",
            user_id="usr_cliente_002",
            shipping_address="Calle Dos 2",
            payment_method_id="pm_test",
            total_price=Decimal("40.00"),
            status="paid",
            created_at=momento,
            items=[
                OrderItemDB(
                    product_id="prod_002",
                    size="L",
                    quantity=2,
                    unit_price=Decimal("20.00")
                )
            ]
        )

        db.add_all([pedido_1, pedido_2])
        db.commit()


# ============================================================
# TEST 1 - ADMIN CONSULTA TODOS LOS PEDIDOS
# ============================================================

def test_admin_consulta_pedidos(client):

    crear_pedidos_prueba()
    autenticar(ADMIN)

    respuesta = client.get("/orders")

    assert respuesta.status_code == 200, respuesta.text

    pedidos = respuesta.json()

    assert len(pedidos) == 2

    usuarios = {
        pedido["user_id"]
        for pedido in pedidos
    }

    assert usuarios == {
        "usr_cliente_001",
        "usr_cliente_002"
    }


# ============================================================
# TEST 2 - PEDIDOS ORDENADOS POR FECHA
# ============================================================

def test_pedidos_ordenados(client):

    crear_pedidos_prueba()
    autenticar(ADMIN)

    respuesta = client.get("/orders")

    assert respuesta.status_code == 200

    pedidos = respuesta.json()

    assert pedidos[0]["id"] == "ord_admin_002"
    assert pedidos[1]["id"] == "ord_admin_001"
    assert pedidos[0]["items"][0]["quantity"] == 2


# ============================================================
# TEST 3 - CLIENTE NO PUEDE CONSULTAR TODOS
# ============================================================

def test_cliente_no_consulta_todos(client):

    crear_pedidos_prueba()
    autenticar(CLIENTE)

    respuesta = client.get("/orders")

    assert respuesta.status_code == 403


# ============================================================
# TEST 4 - SIN AUTENTICACION
# ============================================================

def test_consulta_global_sin_token(client):

    respuesta = client.get("/orders")

    assert respuesta.status_code == 401


# ============================================================
# TEST 5 - LISTADO VACIO
# ============================================================

def test_listado_global_vacio(client):

    autenticar(ADMIN)

    respuesta = client.get("/orders")

    assert respuesta.status_code == 200
    assert respuesta.json() == []
