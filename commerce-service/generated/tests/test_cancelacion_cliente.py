
import pytest

from openapi_server.main import app
from openapi_server.security_api import (
    obtener_administrador,
    obtener_usuario_actual
)
from openapi_server.apis import pedidos_api


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


# ============================================================
# TEST 1 - CLIENTE CANCELA SU PEDIDO
# ============================================================

def test_cliente_cancela_pedido_pendiente(
    client,
    autenticar_cliente
):

    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    assert obtener_stock(client, producto["id"]) == 8

    respuesta = client.post(
        f"/orders/{pedido['id']}/cancel"
    )

    assert respuesta.status_code == 200, respuesta.text

    detalle = client.get(
        f"/orders/{pedido['id']}"
    )

    assert detalle.json()["status"] == "cancelled"
    assert obtener_stock(client, producto["id"]) == 10


# ============================================================
# TEST 2 - IMPEDIR CANCELAR PEDIDOS AJENOS
# ============================================================

def test_cliente_no_cancela_pedido_ajeno(
    client,
    autenticar_cliente
):

    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    app.dependency_overrides[
        obtener_usuario_actual
    ] = lambda: OTRO_CLIENTE

    respuesta = client.post(
        f"/orders/{pedido['id']}/cancel"
    )

    assert respuesta.status_code == 403
    assert obtener_stock(client, producto["id"]) == 8


# ============================================================
# TEST 3 - IMPEDIR CANCELAR PEDIDO PAGADO
# ============================================================

def test_cliente_no_cancela_pedido_pagado(
    client,
    autenticar_cliente
):

    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    app.dependency_overrides[
        obtener_administrador
    ] = lambda: ADMIN

    pago = client.put(
        f"/orders/{pedido['id']}/status",
        json={"status": "paid"}
    )

    assert pago.status_code == 200

    respuesta = client.post(
        f"/orders/{pedido['id']}/cancel"
    )

    assert respuesta.status_code == 409
    assert obtener_stock(client, producto["id"]) == 8


# ============================================================
# TEST 4 - CANCELACION REPETIDA
# ============================================================

def test_cancelacion_repetida_no_duplica_stock(
    client,
    autenticar_cliente
):

    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    primera = client.post(
        f"/orders/{pedido['id']}/cancel"
    )

    segunda = client.post(
        f"/orders/{pedido['id']}/cancel"
    )

    assert primera.status_code == 200
    assert segunda.status_code == 200

    assert obtener_stock(client, producto["id"]) == 10
