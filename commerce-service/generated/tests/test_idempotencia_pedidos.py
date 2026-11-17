
import pytest

from openapi_server.main import app
from openapi_server.apis import pedidos_api
from openapi_server.security_api import (
    obtener_administrador,
    obtener_usuario_actual
)


CLIENTE = {
    "id": "usr_cliente_test",
    "role": "client"
}

ADMIN = {
    "id": "usr_admin_test",
    "role": "admin"
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
                    {"size": "M", "stock": 10}
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


def datos_pedido(producto_id, cantidad=2):

    return {
        "user_id": CLIENTE["id"],
        "items": [
            {
                "product_id": producto_id,
                "size": "M",
                "quantity": cantidad,
                "unit_price": 25.0
            }
        ],
        "shipping_address": "Calle Mayor 12",
        "payment_method_id": "pm_test"
    }


def crear_pedido(
    client,
    producto_id,
    clave=None,
    cantidad=2
):

    headers = {
        "Authorization": "Bearer token_de_prueba"
    }

    if clave is not None:
        headers["Idempotency-Key"] = clave

    return client.post(
        "/orders",
        json=datos_pedido(producto_id, cantidad),
        headers=headers
    )


def obtener_stock(client, producto_id):

    respuesta = client.get(
        f"/products/{producto_id}"
    )

    assert respuesta.status_code == 200
    return respuesta.json()["variants"][0]["stock"]


# ============================================================
# TEST 1 - MISMA CLAVE, MISMO PEDIDO
# ============================================================

def test_reintento_no_duplica_pedido(
    client,
    autenticar_cliente
):

    producto = crear_producto(client)

    primera = crear_pedido(
        client,
        producto["id"],
        clave="compra-001"
    )

    segunda = crear_pedido(
        client,
        producto["id"],
        clave="compra-001"
    )

    assert primera.status_code == 201, primera.text
    assert segunda.status_code == 201, segunda.text

    assert primera.json()["id"] == segunda.json()["id"]

    # Solo deben descontarse dos unidades.
    assert obtener_stock(client, producto["id"]) == 8

    historial = client.get(
        f"/orders/user/{CLIENTE['id']}"
    )

    assert historial.status_code == 200
    assert len(historial.json()) == 1


# ============================================================
# TEST 2 - MISMA CLAVE, COMPRA DIFERENTE
# ============================================================

def test_no_reutilizar_clave_con_otra_compra(
    client,
    autenticar_cliente
):

    producto = crear_producto(client)

    primera = crear_pedido(
        client,
        producto["id"],
        clave="compra-002",
        cantidad=2
    )

    segunda = crear_pedido(
        client,
        producto["id"],
        clave="compra-002",
        cantidad=3
    )

    assert primera.status_code == 201
    assert segunda.status_code == 409

    assert obtener_stock(client, producto["id"]) == 8


# ============================================================
# TEST 3 - CLAVES DIFERENTES
# ============================================================

def test_claves_diferentes_crean_pedidos_distintos(
    client,
    autenticar_cliente
):

    producto = crear_producto(client)

    primera = crear_pedido(
        client,
        producto["id"],
        clave="compra-003"
    )

    segunda = crear_pedido(
        client,
        producto["id"],
        clave="compra-004"
    )

    assert primera.status_code == 201
    assert segunda.status_code == 201

    assert primera.json()["id"] != segunda.json()["id"]
    assert obtener_stock(client, producto["id"]) == 6


# ============================================================
# TEST 4 - COMPATIBILIDAD SIN CLAVE
# ============================================================

def test_pedidos_sin_clave_siguen_funcionando(
    client,
    autenticar_cliente
):

    producto = crear_producto(client)

    primera = crear_pedido(
        client,
        producto["id"]
    )

    segunda = crear_pedido(
        client,
        producto["id"]
    )

    assert primera.status_code == 201
    assert segunda.status_code == 201

    assert primera.json()["id"] != segunda.json()["id"]
    assert obtener_stock(client, producto["id"]) == 6
