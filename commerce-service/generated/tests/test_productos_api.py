
import pytest

from openapi_server.main import app
from openapi_server.security_api import obtener_administrador


# ============================================================
# DATOS DE PRUEBA
# ============================================================

PRODUCTO_VALIDO = {
    "name": "Sudadera Oficial Subsonic",
    "description": "Sudadera negra con logotipo",
    "category": "ropa",
    "price": 45.00,
    "images": [
        "https://example.com/sudadera.jpg"
    ],
    "variants": [
        {"size": "S", "stock": 10},
        {"size": "M", "stock": 20},
        {"size": "L", "stock": 5}
    ]
}


# ============================================================
# FIXTURE ADMINISTRADOR
# ============================================================

@pytest.fixture
def admin():
    app.dependency_overrides[obtener_administrador] = (
        lambda: {
            "id": "usr_admin_test",
            "role": "admin"
        }
    )

    yield

    app.dependency_overrides.pop(
        obtener_administrador,
        None
    )


def crear_producto(client):
    respuesta = client.post(
        "/products",
        json=PRODUCTO_VALIDO
    )

    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


# ============================================================
# TESTS DE PRODUCTOS
# ============================================================

def test_catalogo_inicial_vacio(client):
    respuesta = client.get("/products")

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_crear_producto_como_admin(client, admin):
    producto = crear_producto(client)

    assert producto["id"].startswith("prod_")
    assert producto["name"] == "Sudadera Oficial Subsonic"
    assert producto["category"] == "ropa"
    assert producto["price"] == 45.0
    assert len(producto["variants"]) == 3


def test_crear_producto_sin_autenticacion(client):
    respuesta = client.post(
        "/products",
        json=PRODUCTO_VALIDO
    )

    assert respuesta.status_code == 401


def test_listar_productos(client, admin):
    crear_producto(client)

    respuesta = client.get("/products")

    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 1


def test_filtrar_productos_por_categoria(client, admin):
    crear_producto(client)

    respuesta = client.post(
        "/products",
        json={
            "name": "Gorra Subsonic",
            "category": "accesorios",
            "price": 15.0,
            "variants": [
                {"size": "unica", "stock": 8}
            ]
        }
    )

    assert respuesta.status_code == 201

    filtrados = client.get(
        "/products",
        params={"category": "ropa"}
    )

    assert filtrados.status_code == 200
    assert len(filtrados.json()) == 1
    assert filtrados.json()[0]["category"] == "ropa"


def test_consultar_producto_por_id(client, admin):
    producto = crear_producto(client)

    respuesta = client.get(
        f"/products/{producto['id']}"
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == producto["id"]


def test_consultar_producto_inexistente(client):
    respuesta = client.get(
        "/products/prod_inexistente"
    )

    assert respuesta.status_code == 404


def test_actualizar_producto(client, admin):
    producto = crear_producto(client)

    nuevos_datos = {
        "name": "Sudadera Subsonic Actualizada",
        "description": "Nueva version",
        "category": "ropa",
        "price": 49.99,
        "variants": [
            {"size": "M", "stock": 30}
        ]
    }

    respuesta = client.put(
        f"/products/{producto['id']}",
        json=nuevos_datos
    )

    assert respuesta.status_code == 200, respuesta.text

    actualizado = respuesta.json()

    assert actualizado["name"] == nuevos_datos["name"]
    assert actualizado["price"] == 49.99
    assert len(actualizado["variants"]) == 1
    assert actualizado["variants"][0]["stock"] == 30


def test_actualizar_producto_inexistente(client, admin):
    respuesta = client.put(
        "/products/prod_inexistente",
        json=PRODUCTO_VALIDO
    )

    assert respuesta.status_code == 404


def test_eliminar_producto(client, admin):
    producto = crear_producto(client)

    respuesta = client.delete(
        f"/products/{producto['id']}"
    )

    assert respuesta.status_code == 204

    consulta = client.get(
        f"/products/{producto['id']}"
    )

    assert consulta.status_code == 404


def test_eliminar_producto_inexistente(client, admin):
    respuesta = client.delete(
        "/products/prod_inexistente"
    )

    assert respuesta.status_code == 404


def test_rechazar_precio_negativo(client, admin):
    datos = PRODUCTO_VALIDO.copy()
    datos["price"] = -10

    respuesta = client.post(
        "/products",
        json=datos
    )

    assert respuesta.status_code == 400


def test_rechazar_stock_negativo(client, admin):
    datos = PRODUCTO_VALIDO.copy()
    datos["variants"] = [
        {"size": "M", "stock": -5}
    ]

    respuesta = client.post(
        "/products",
        json=datos
    )

    assert respuesta.status_code == 400


def test_rechazar_tallas_duplicadas(client, admin):
    datos = PRODUCTO_VALIDO.copy()
    datos["variants"] = [
        {"size": "M", "stock": 10},
        {"size": "M", "stock": 20}
    ]

    respuesta = client.post(
        "/products",
        json=datos
    )

    assert respuesta.status_code == 400


def test_rechazar_nombre_vacio(client, admin):
    datos = PRODUCTO_VALIDO.copy()
    datos["name"] = "   "

    respuesta = client.post(
        "/products",
        json=datos
    )

    assert respuesta.status_code == 400


def test_rechazar_precio_con_tres_decimales(client, admin):
    datos = PRODUCTO_VALIDO.copy()
    datos["price"] = 15.999

    respuesta = client.post(
        "/products",
        json=datos
    )

    assert respuesta.status_code == 400


def test_actualizacion_sin_variantes_conserva_stock(client, admin):
    producto = crear_producto(client)

    respuesta = client.put(
        f"/products/{producto['id']}",
        json={
            "name": "Sudadera Renovada",
            "category": "ropa",
            "price": 50.0
        }
    )

    assert respuesta.status_code == 200, respuesta.text

    actualizado = respuesta.json()

    assert len(actualizado["variants"]) == 3

    stocks = {
        variante["size"]: variante["stock"]
        for variante in actualizado["variants"]
    }

    assert stocks == {
        "S": 10,
        "M": 20,
        "L": 5
    }
