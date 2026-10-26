from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from fastapi.testclient import TestClient
import pytest

from openapi_server.main import app
from openapi_server.security_api import (
    obtener_administrador,
    obtener_usuario_actual
)
from openapi_server.apis import pedidos_api


# ============================================================
# DATOS DE PRUEBA
# ============================================================

ADMIN = {
    "id": "usr_admin_test",
    "role": "admin"
}

CLIENTE = {
    "id": "usr_cliente_test",
    "role": "client"
}

OTRO_CLIENTE = {
    "id": "usr_otro_cliente",
    "role": "client"
}

PRODUCTO = {
    "name": "Camiseta Oficial Subsonic",
    "description": "Camiseta negra del festival",
    "category": "ropa",
    "price": 25.00,
    "variants": [
        {"size": "S", "stock": 5},
        {"size": "M", "stock": 10}
    ]
}


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def admin():
    app.dependency_overrides[obtener_administrador] = (
        lambda: ADMIN
    )

    yield

    app.dependency_overrides.pop(
        obtener_administrador,
        None
    )


@pytest.fixture
def cliente(monkeypatch):
    app.dependency_overrides[obtener_usuario_actual] = (
        lambda: CLIENTE
    )

    # Simular solamente la consulta a auth-service.
    async def validar_comprador_simulado(user_id, credentials):
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

    app.dependency_overrides.pop(
        obtener_usuario_actual,
        None
    )


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def crear_producto(client):
    app.dependency_overrides[obtener_administrador] = (
        lambda: ADMIN
    )

    respuesta = client.post(
        "/products",
        json=PRODUCTO
    )

    assert respuesta.status_code == 201, respuesta.text

    app.dependency_overrides.pop(
        obtener_administrador,
        None
    )

    return respuesta.json()


def datos_pedido(producto_id, cantidad=2, talla="M"):
    return {
        "user_id": CLIENTE["id"],
        "items": [
            {
                "product_id": producto_id,
                "size": talla,
                "quantity": cantidad,
                "unit_price": 0.01
            }
        ],
        "shipping_address": "Calle Mayor 12, Madrid",
        "payment_method_id": "pm_test"
    }


def crear_pedido(client, producto_id):
    respuesta = client.post(
        "/orders",
        json=datos_pedido(producto_id)
    )

    assert respuesta.status_code == 201, respuesta.text

    return respuesta.json()


def obtener_stock(client, producto_id, talla):
    respuesta = client.get(
        f"/products/{producto_id}"
    )

    assert respuesta.status_code == 200

    for variante in respuesta.json()["variants"]:
        if variante["size"] == talla:
            return variante["stock"]

    raise AssertionError("Talla no encontrada")


# ============================================================
# TESTS DE PEDIDOS
# ============================================================

def test_crear_pedido_correctamente(client, cliente):
    producto = crear_producto(client)

    respuesta = client.post(
        "/orders",
        json=datos_pedido(producto["id"])
    )

    assert respuesta.status_code == 201, respuesta.text

    pedido = respuesta.json()

    assert pedido["id"].startswith("ord_")
    assert pedido["user_id"] == CLIENTE["id"]
    assert pedido["status"] == "pending"
    assert len(pedido["items"]) == 1
    assert pedido["items"][0]["quantity"] == 2
    assert pedido["created_at"] is not None


def test_compra_descontar_stock(client, cliente):
    producto = crear_producto(client)

    assert obtener_stock(client, producto["id"], "M") == 10

    crear_pedido(client, producto["id"])

    assert obtener_stock(client, producto["id"], "M") == 8


def test_precio_no_puede_manipularse(client, cliente):
    producto = crear_producto(client)

    respuesta = client.post(
        "/orders",
        json=datos_pedido(producto["id"])
    )

    assert respuesta.status_code == 201, respuesta.text

    pedido = respuesta.json()

    # El comprador envia 0.01, pero el precio
    # almacenado realmente es 25 euros.
    assert pedido["items"][0]["unit_price"] == 25.0
    assert pedido["total_price"] == 50.0


def test_stock_insuficiente_devuelve_409(client, cliente):
    producto = crear_producto(client)

    respuesta = client.post(
        "/orders",
        json=datos_pedido(
            producto["id"],
            cantidad=100
        )
    )

    assert respuesta.status_code == 409

    # La compra fallida no descuenta inventario.
    assert obtener_stock(client, producto["id"], "M") == 10


def test_cantidad_cero_rechazada(client, cliente):
    producto = crear_producto(client)

    respuesta = client.post(
        "/orders",
        json=datos_pedido(
            producto["id"],
            cantidad=0
        )
    )

    assert respuesta.status_code == 400


def test_cantidad_negativa_rechazada(client, cliente):
    producto = crear_producto(client)

    respuesta = client.post(
        "/orders",
        json=datos_pedido(
            producto["id"],
            cantidad=-2
        )
    )

    assert respuesta.status_code == 400


def test_talla_inexistente_rechazada(client, cliente):
    producto = crear_producto(client)

    respuesta = client.post(
        "/orders",
        json=datos_pedido(
            producto["id"],
            talla="XXL"
        )
    )

    assert respuesta.status_code == 400


def test_producto_inexistente_rechazado(client, cliente):
    respuesta = client.post(
        "/orders",
        json=datos_pedido("prod_inexistente")
    )

    assert respuesta.status_code == 400


def test_direccion_vacia_rechazada(client, cliente):
    producto = crear_producto(client)

    datos = datos_pedido(producto["id"])
    datos["shipping_address"] = "   "

    respuesta = client.post(
        "/orders",
        json=datos
    )

    assert respuesta.status_code == 400


def test_no_permitir_comprar_para_otro_usuario(
    client,
    cliente
):
    producto = crear_producto(client)

    datos = datos_pedido(producto["id"])
    datos["user_id"] = OTRO_CLIENTE["id"]

    respuesta = client.post(
        "/orders",
        json=datos
    )

    assert respuesta.status_code == 403
    assert obtener_stock(client, producto["id"], "M") == 10


def test_consultar_historial_propio(client, cliente):
    producto = crear_producto(client)

    crear_pedido(client, producto["id"])

    respuesta = client.get(
        f"/orders/user/{CLIENTE['id']}"
    )

    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 1


def test_no_consultar_historial_ajeno(client, cliente):
    respuesta = client.get(
        f"/orders/user/{OTRO_CLIENTE['id']}"
    )

    assert respuesta.status_code == 403


def test_consultar_pedido_por_id(client, cliente):
    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    respuesta = client.get(
        f"/orders/{pedido['id']}"
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == pedido["id"]


def test_pedido_inexistente_devuelve_404(client, cliente):
    respuesta = client.get(
        "/orders/ord_inexistente"
    )

    assert respuesta.status_code == 404



def test_actualizar_estado_como_admin(client, cliente):
    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    app.dependency_overrides[obtener_administrador] = (
        lambda: ADMIN
    )

    # Avanzar por los estados permitidos.
    for estado in ["paid", "preparing", "shipped"]:
        respuesta = client.put(
            f"/orders/{pedido['id']}/status",
            json={"status": estado}
        )

        assert respuesta.status_code == 200, respuesta.text

        detalle = client.get(
            f"/orders/{pedido['id']}"
        )

        assert detalle.status_code == 200
        assert detalle.json()["status"] == estado

    # El pedido debe haber terminado en shipped.
    detalle = client.get(
        f"/orders/{pedido['id']}"
    )

    assert detalle.json()["status"] == "shipped"



def test_actualizar_estado_sin_admin(client, cliente):
    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    respuesta = client.put(
        f"/orders/{pedido['id']}/status",
        json={"status": "shipped"}
    )

    # El usuario esta autenticado, pero no es administrador.
    assert respuesta.status_code == 403


def test_pedido_sin_autenticacion(client):
    respuesta = client.post(
        "/orders",
        json={
            "user_id": CLIENTE["id"],
            "items": [
                {
                    "product_id": "prod_test",
                    "size": "M",
                    "quantity": 1,
                    "unit_price": 25.0
                }
            ],
            "shipping_address": "Calle Mayor 12"
        }
    )

    assert respuesta.status_code == 401


def test_compra_repetida_sin_stock(client, cliente):
    producto = crear_producto(client)

    primera = client.post(
        "/orders",
        json=datos_pedido(
            producto["id"],
            cantidad=8
        )
    )

    assert primera.status_code == 201, primera.text

    segunda = client.post(
        "/orders",
        json=datos_pedido(
            producto["id"],
            cantidad=5
        )
    )

    assert segunda.status_code == 409

    # Solo se descuenta el stock de la primera compra.
    assert obtener_stock(client, producto["id"], "M") == 2


def test_productos_repetidos_se_agrupan(client, cliente):
    producto = crear_producto(client)

    datos = datos_pedido(producto["id"])

    datos["items"].append({
        "product_id": producto["id"],
        "size": "M",
        "quantity": 3,
        "unit_price": 0.01
    })

    respuesta = client.post(
        "/orders",
        json=datos
    )

    assert respuesta.status_code == 201, respuesta.text

    pedido = respuesta.json()

    assert len(pedido["items"]) == 1
    assert pedido["items"][0]["quantity"] == 5
    assert pedido["total_price"] == 125.0

    assert obtener_stock(client, producto["id"], "M") == 5


def test_compra_fallida_no_modifica_ningun_stock(
    client,
    cliente
):
    producto = crear_producto(client)

    datos = datos_pedido(
        producto["id"],
        cantidad=2,
        talla="S"
    )

    # La talla S tiene stock 5 y la M stock 10.
    # La segunda linea debe hacer fallar toda la compra.
    datos["items"].append({
        "product_id": producto["id"],
        "size": "M",
        "quantity": 100,
        "unit_price": 0.01
    })

    respuesta = client.post(
        "/orders",
        json=datos
    )

    assert respuesta.status_code == 409

    assert obtener_stock(client, producto["id"], "S") == 5
    assert obtener_stock(client, producto["id"], "M") == 10

    historial = client.get(
        f"/orders/user/{CLIENTE['id']}"
    )

    assert historial.status_code == 200
    assert historial.json() == []


# ============================================================
# TESTS DE CANCELACION Y CICLO DE VIDA DE PEDIDOS
# ============================================================

def test_cancelar_pedido_devuelve_stock(client, cliente):
    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    # La compra de 2 unidades deja 8 disponibles.
    assert obtener_stock(client, producto["id"], "M") == 8

    app.dependency_overrides[obtener_administrador] = (
        lambda: ADMIN
    )

    respuesta = client.put(
        f"/orders/{pedido['id']}/status",
        json={"status": "cancelled"}
    )

    assert respuesta.status_code == 200, respuesta.text

    # Las dos unidades deben regresar al inventario.
    assert obtener_stock(client, producto["id"], "M") == 10

    detalle = client.get(f"/orders/{pedido['id']}")
    assert detalle.json()["status"] == "cancelled"


def test_cancelar_dos_veces_no_duplica_stock(client, cliente):
    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    app.dependency_overrides[obtener_administrador] = (
        lambda: ADMIN
    )

    for _ in range(2):
        respuesta = client.put(
            f"/orders/{pedido['id']}/status",
            json={"status": "cancelled"}
        )

        assert respuesta.status_code == 200, respuesta.text

    assert obtener_stock(client, producto["id"], "M") == 10


def test_no_permitir_salto_de_estados(client, cliente):
    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    app.dependency_overrides[obtener_administrador] = (
        lambda: ADMIN
    )

    respuesta = client.put(
        f"/orders/{pedido['id']}/status",
        json={"status": "delivered"}
    )

    assert respuesta.status_code == 409

    detalle = client.get(f"/orders/{pedido['id']}")
    assert detalle.json()["status"] == "pending"


def test_no_cancelar_pedido_pagado(client, cliente):
    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    app.dependency_overrides[obtener_administrador] = (
        lambda: ADMIN
    )

    pago = client.put(
        f"/orders/{pedido['id']}/status",
        json={"status": "paid"}
    )

    assert pago.status_code == 200

    cancelacion = client.put(
        f"/orders/{pedido['id']}/status",
        json={"status": "cancelled"}
    )

    assert cancelacion.status_code == 409

    # El pedido sigue reservado y el stock no cambia.
    assert obtener_stock(client, producto["id"], "M") == 8


def test_pedido_cancelado_no_puede_reactivarse(
    client,
    cliente
):
    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    app.dependency_overrides[obtener_administrador] = (
        lambda: ADMIN
    )

    cancelacion = client.put(
        f"/orders/{pedido['id']}/status",
        json={"status": "cancelled"}
    )

    assert cancelacion.status_code == 200

    reactivacion = client.put(
        f"/orders/{pedido['id']}/status",
        json={"status": "paid"}
    )

    assert reactivacion.status_code == 409

    assert obtener_stock(client, producto["id"], "M") == 10


def test_no_eliminar_producto_con_pedido_pendiente(
    client,
    cliente
):
    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    app.dependency_overrides[obtener_administrador] = (
        lambda: ADMIN
    )

    # El producto pertenece a un pedido pendiente.
    eliminado = client.delete(
        f"/products/{producto['id']}"
    )

    # No debe permitirse eliminarlo.
    assert eliminado.status_code == 409

    # El producto y el stock siguen disponibles.
    assert obtener_stock(client, producto["id"], "M") == 8

    # Ahora podemos cancelar el pedido correctamente.
    cancelacion = client.put(
        f"/orders/{pedido['id']}/status",
        json={"status": "cancelled"}
    )

    assert cancelacion.status_code == 200

    # Las unidades se devuelven al inventario.
    assert obtener_stock(client, producto["id"], "M") == 10



def test_no_modificar_tallas_con_pedido_pendiente(
    client,
    cliente
):
    producto = crear_producto(client)
    pedido = crear_pedido(client, producto["id"])

    app.dependency_overrides[obtener_administrador] = (
        lambda: ADMIN
    )

    # Intentar eliminar la talla M de un producto
    # que ya tiene unidades reservadas.
    respuesta = client.put(
        f"/products/{producto['id']}",
        json={
            "name": "Camiseta Subsonic Actualizada",
            "category": "ropa",
            "price": 30.0,
            "variants": [
                {"size": "S", "stock": 5}
            ]
        }
    )

    assert respuesta.status_code == 409

    # El inventario anterior debe conservarse.
    assert obtener_stock(client, producto["id"], "M") == 8

    # La cancelacion debe seguir siendo posible.
    cancelacion = client.put(
        f"/orders/{pedido['id']}/status",
        json={"status": "cancelled"}
    )

    assert cancelacion.status_code == 200
    assert obtener_stock(client, producto["id"], "M") == 10


# ============================================================
# TEST DE COMPRAS SIMULTANEAS
# ============================================================

def test_compras_simultaneas_no_superan_stock(client, cliente):
    producto = crear_producto(client)
    producto_id = producto["id"]

    # La talla M tiene inicialmente 10 unidades.
    assert obtener_stock(client, producto_id, "M") == 10

    # Sincronizar los dos compradores para que envien
    # sus peticiones de forma concurrente.
    barrera = Barrier(3, timeout=10)

    def realizar_compra():
        datos = datos_pedido(
            producto_id,
            cantidad=7,
            talla="M"
        )

        # Cada hilo utiliza su propio TestClient.
        with TestClient(app) as cliente_http:
            barrera.wait()

            respuesta = cliente_http.post(
                "/orders",
                json=datos
            )

            return respuesta.status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        compra_1 = executor.submit(realizar_compra)
        compra_2 = executor.submit(realizar_compra)

        # Liberar ambas peticiones al mismo tiempo.
        barrera.wait()

        resultados = [
            compra_1.result(timeout=15),
            compra_2.result(timeout=15)
        ]

    # Solo una compra puede completarse.
    assert sorted(resultados) == [201, 409]

    # Se descuentan solamente 7 unidades.
    assert obtener_stock(client, producto_id, "M") == 3

    # Solo debe existir un pedido registrado.
    historial = client.get(
        f"/orders/user/{CLIENTE['id']}"
    )

    assert historial.status_code == 200
    assert len(historial.json()) == 1
    assert historial.json()[0]["items"][0]["quantity"] == 7
