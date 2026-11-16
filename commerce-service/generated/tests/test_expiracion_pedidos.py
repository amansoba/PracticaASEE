
from datetime import datetime, timedelta, timezone

import pytest

from openapi_server.main import app
from openapi_server.database import SessionLocal
from openapi_server.db_models import OrderDB
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


def cambiar_antiguedad(pedido_id, minutos):

    with SessionLocal() as db:
        pedido = db.get(OrderDB, pedido_id)

        assert pedido is not None

        pedido.created_at = (
            datetime.now(timezone.utc)
            - timedelta(minutes=minutos)
        )

        db.commit()


def consultar_estado(pedido_id):

    with SessionLocal() as db:
        pedido = db.get(OrderDB, pedido_id)

        assert pedido is not None
        return pedido.status


def ejecutar_caducidad():
    # La funcion se implementara despues de
    # comprobar que estas pruebas fallan.
    from openapi_server.impl.pedidos_impl import (
        expirar_pedidos_pendientes
    )

    return expirar_pedidos_pendientes()


# ============================================================
# TEST 1 - EXPIRAR PEDIDO ANTIGUO
# ============================================================

def test_pedido_pendiente_caducado_devuelve_stock(
    client,
    autenticar_cliente
):

    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    assert obtener_stock(client, producto["id"]) == 8

    cambiar_antiguedad(
        pedido["id"],
        minutos=31
    )

    expirados = ejecutar_caducidad()

    assert expirados == 1
    assert consultar_estado(pedido["id"]) == "cancelled"
    assert obtener_stock(client, producto["id"]) == 10


# ============================================================
# TEST 2 - NO EXPIRAR PEDIDO RECIENTE
# ============================================================

def test_pedido_reciente_no_caduca(
    client,
    autenticar_cliente
):

    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    cambiar_antiguedad(
        pedido["id"],
        minutos=20
    )

    expirados = ejecutar_caducidad()

    assert expirados == 0
    assert consultar_estado(pedido["id"]) == "pending"
    assert obtener_stock(client, producto["id"]) == 8


# ============================================================
# TEST 3 - NO EXPIRAR PEDIDO PAGADO
# ============================================================

def test_pedido_pagado_no_caduca(
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

    cambiar_antiguedad(
        pedido["id"],
        minutos=31
    )

    expirados = ejecutar_caducidad()

    assert expirados == 0
    assert consultar_estado(pedido["id"]) == "paid"
    assert obtener_stock(client, producto["id"]) == 8


# ============================================================
# TEST 4 - NO DEVOLVER STOCK DOS VECES
# ============================================================

def test_expiracion_repetida_no_duplica_stock(
    client,
    autenticar_cliente
):

    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    cambiar_antiguedad(
        pedido["id"],
        minutos=31
    )

    primera = ejecutar_caducidad()
    segunda = ejecutar_caducidad()

    assert primera == 1
    assert segunda == 0

    assert consultar_estado(pedido["id"]) == "cancelled"
    assert obtener_stock(client, producto["id"]) == 10
