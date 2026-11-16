
import pytest

from openapi_server.main import app
from openapi_server.security_api import (
    obtener_administrador,
    obtener_usuario_actual
)
from openapi_server.apis import pedidos_api


# ============================================================
# USUARIOS SIMULADOS
# ============================================================

CLIENTE = {
    "id": "usr_cliente_test",
    "role": "client"
}

OTRO_CLIENTE = {
    "id": "usr_otro_cliente",
    "role": "client"
}

ADMIN = {
    "id": "usr_admin_test",
    "role": "admin"
}

HEADERS = {
    "Authorization": "Bearer token_de_prueba"
}


# ============================================================
# AUTENTICACION SIMULADA
# ============================================================

@pytest.fixture
def autenticar_cliente(monkeypatch):

    app.dependency_overrides[
        obtener_usuario_actual
    ] = lambda: CLIENTE

    async def validar_comprador_simulado(
        user_id,
        credentials
    ):
        return {
            "id": user_id,
            "role": "client"
        }

    monkeypatch.setattr(
        pedidos_api,
        "validar_comprador",
        validar_comprador_simulado
    )

    yield

    app.dependency_overrides.clear()


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def crear_producto(client):

    app.dependency_overrides[
        obtener_administrador
    ] = lambda: ADMIN

    try:
        respuesta = client.post(
            "/products",
            json={
                "name": "Camiseta Subsonic",
                "description": "Camiseta oficial",
                "category": "ropa",
                "price": 25.0,
                "variants": [
                    {
                        "size": "M",
                        "stock": 10
                    }
                ]
            }
        )

        assert respuesta.status_code == 201, respuesta.text

        return respuesta.json()

    finally:
        app.dependency_overrides.pop(
            obtener_administrador,
            None
        )


def crear_pedido(client, producto_id):

    respuesta = client.post(
        "/orders",
        headers=HEADERS,
        json={
            "user_id": CLIENTE["id"],
            "items": [
                {
                    "product_id": producto_id,
                    "size": "M",
                    "quantity": 2,
                    "unit_price": 25.0
                }
            ],
            "shipping_address": "Calle Mayor 12",
            "payment_method_id": "pm_test"
        }
    )

    assert respuesta.status_code == 201, respuesta.text

    return respuesta.json()


def obtener_stock(client, producto_id):

    respuesta = client.get(
        f"/products/{producto_id}"
    )

    assert respuesta.status_code == 200

    return respuesta.json()["variants"][0]["stock"]


def pagar_pedido(client, pedido_id, token="tok_test_success"):

    return client.post(
        f"/orders/{pedido_id}/pay",
        json={
            "payment_token": token
        }
    )


# ============================================================
# TEST 1 - PAGO CORRECTO
# ============================================================

def test_cliente_paga_pedido_pendiente(
    client,
    autenticar_cliente
):

    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    assert pedido["status"] == "pending"
    assert obtener_stock(client, producto["id"]) == 8

    respuesta = pagar_pedido(
        client,
        pedido["id"]
    )

    assert respuesta.status_code == 200, respuesta.text

    detalle = client.get(
        f"/orders/{pedido['id']}"
    )

    assert detalle.status_code == 200
    assert detalle.json()["status"] == "paid"

    # El pago no debe volver a descontar stock.
    assert obtener_stock(client, producto["id"]) == 8


# ============================================================
# TEST 2 - PAGO RECHAZADO
# ============================================================

def test_pago_simulado_rechazado(
    client,
    autenticar_cliente
):

    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    respuesta = pagar_pedido(
        client,
        pedido["id"],
        token="tok_test_declined"
    )

    assert respuesta.status_code == 400

    detalle = client.get(
        f"/orders/{pedido['id']}"
    )

    assert detalle.json()["status"] == "pending"
    assert obtener_stock(client, producto["id"]) == 8


# ============================================================
# TEST 3 - NO PAGAR PEDIDOS AJENOS
# ============================================================

def test_cliente_no_paga_pedido_ajeno(
    client,
    autenticar_cliente
):

    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    app.dependency_overrides[
        obtener_usuario_actual
    ] = lambda: OTRO_CLIENTE

    respuesta = pagar_pedido(
        client,
        pedido["id"]
    )

    assert respuesta.status_code == 403


# ============================================================
# TEST 4 - NO PAGAR PEDIDOS CANCELADOS
# ============================================================

def test_no_pagar_pedido_cancelado(
    client,
    autenticar_cliente
):

    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    cancelacion = client.post(
        f"/orders/{pedido['id']}/cancel"
    )

    assert cancelacion.status_code == 200

    respuesta = pagar_pedido(
        client,
        pedido["id"]
    )

    assert respuesta.status_code == 409

    detalle = client.get(
        f"/orders/{pedido['id']}"
    )

    assert detalle.json()["status"] == "cancelled"
    assert obtener_stock(client, producto["id"]) == 10


# ============================================================
# TEST 5 - NO PAGAR DOS VECES
# ============================================================

def test_no_pagar_dos_veces(
    client,
    autenticar_cliente
):

    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    primera = pagar_pedido(
        client,
        pedido["id"]
    )

    segunda = pagar_pedido(
        client,
        pedido["id"]
    )

    assert primera.status_code == 200
    assert segunda.status_code == 409

    detalle = client.get(
        f"/orders/{pedido['id']}"
    )

    assert detalle.json()["status"] == "paid"
    assert obtener_stock(client, producto["id"]) == 8


# ============================================================
# TEST 6 - PEDIDO INEXISTENTE
# ============================================================

def test_pagar_pedido_inexistente(
    client,
    autenticar_cliente
):

    respuesta = pagar_pedido(
        client,
        "ord_inexistente"
    )

    assert respuesta.status_code == 404
