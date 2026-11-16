
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from fastapi.testclient import TestClient

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

HEADERS = {
    "Authorization": "Bearer token_de_prueba",
    "Idempotency-Key": "compra-concurrente-001"
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


def datos_pedido(producto_id):

    return {
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


# ============================================================
# TEST - DOS PETICIONES SIMULTANEAS
# ============================================================

def test_compras_simultaneas_con_misma_clave(
    client,
    autenticar_cliente
):

    producto = crear_producto(client)

    # Ambas peticiones intentaran realizar
    # exactamente la misma compra.
    solicitud = datos_pedido(producto["id"])

    # Sincronizar los dos hilos para que
    # envien la peticion al mismo tiempo.
    barrera = Barrier(3, timeout=10)

    def comprar():

        with TestClient(app) as cliente_http:

            barrera.wait()

            respuesta = cliente_http.post(
                "/orders",
                json=solicitud,
                headers=HEADERS
            )

            return respuesta

    # Lanzar dos compras concurrentes.
    with ThreadPoolExecutor(max_workers=2) as executor:

        futuro_1 = executor.submit(comprar)
        futuro_2 = executor.submit(comprar)

        # Liberar los dos hilos.
        barrera.wait()

        primera = futuro_1.result(timeout=15)
        segunda = futuro_2.result(timeout=15)

    # Ambas peticiones deben completarse.
    assert primera.status_code == 201, primera.text
    assert segunda.status_code == 201, segunda.text

    # La clave de idempotencia debe hacer
    # que ambas reciban el mismo pedido.
    assert primera.json()["id"] == segunda.json()["id"]

    # El inventario solamente debe descontar
    # las dos unidades de una unica compra.
    respuesta_producto = client.get(
        f"/products/{producto['id']}"
    )

    assert respuesta_producto.status_code == 200

    stock = respuesta_producto.json()["variants"][0]["stock"]

    assert stock == 8

    # Comprobar que PostgreSQL solo
    # ha almacenado un pedido.
    historial = client.get(
        f"/orders/user/{CLIENTE['id']}"
    )

    assert historial.status_code == 200
    assert len(historial.json()) == 1
