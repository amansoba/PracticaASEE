
import httpx
import pytest

from openapi_server import security_api


ADMIN = {
    "id": "usr_admin_test",
    "role": "admin"
}

CLIENTE = {
    "id": "usr_cliente_test",
    "role": "client"
}

PRODUCTO = {
    "name": "Camiseta Subsonic",
    "category": "ropa",
    "price": 25.0,
    "variants": [
        {"size": "M", "stock": 10}
    ]
}

CABECERA = {
    "Authorization": "Bearer token_de_prueba"
}


# ============================================================
# SIMULACION DEL SERVICIO DE AUTENTICACION
# ============================================================

def simular_auth(monkeypatch, respuesta_usuario=None,
                 estado=200, error_conexion=False):

    def responder(request):
        if error_conexion:
            raise httpx.ConnectError(
                "Autenticacion no disponible",
                request=request
            )

        if request.url.path == "/users/me":
            return httpx.Response(
                status_code=estado,
                json=respuesta_usuario or CLIENTE
            )

        if request.url.path.startswith("/users/"):
            return httpx.Response(
                status_code=estado,
                json=respuesta_usuario or CLIENTE
            )

        return httpx.Response(
            status_code=404,
            json={"detail": "No encontrado"}
        )

    transporte = httpx.MockTransport(responder)

    # Guardamos la clase original antes de sustituirla.
    cliente_original = httpx.AsyncClient

    def cliente_simulado(*args, **kwargs):
        kwargs["transport"] = transporte
        return cliente_original(*args, **kwargs)

    monkeypatch.setattr(
        security_api.httpx,
        "AsyncClient",
        cliente_simulado
    )


# ============================================================
# TESTS DE SEGURIDAD
# ============================================================

def test_consulta_publica_sin_token(client):
    respuesta = client.get("/products")

    assert respuesta.status_code == 200


def test_crear_producto_sin_token(client):
    respuesta = client.post(
        "/products",
        json=PRODUCTO
    )

    assert respuesta.status_code == 401


def test_crear_producto_con_cliente(client, monkeypatch):
    simular_auth(monkeypatch, CLIENTE)

    respuesta = client.post(
        "/products",
        json=PRODUCTO,
        headers=CABECERA
    )

    assert respuesta.status_code == 403


def test_crear_producto_con_admin(client, monkeypatch):
    simular_auth(monkeypatch, ADMIN)

    respuesta = client.post(
        "/products",
        json=PRODUCTO,
        headers=CABECERA
    )

    assert respuesta.status_code == 201, respuesta.text


def test_token_invalido(client, monkeypatch):
    simular_auth(
        monkeypatch,
        estado=401
    )

    respuesta = client.post(
        "/products",
        json=PRODUCTO,
        headers=CABECERA
    )

    assert respuesta.status_code == 401


def test_auth_no_disponible(client, monkeypatch):
    simular_auth(
        monkeypatch,
        error_conexion=True
    )

    respuesta = client.post(
        "/products",
        json=PRODUCTO,
        headers=CABECERA
    )

    assert respuesta.status_code == 503


def test_historial_ajeno_prohibido(client, monkeypatch):
    simular_auth(monkeypatch, CLIENTE)

    respuesta = client.get(
        "/orders/user/usr_otro_cliente",
        headers=CABECERA
    )

    assert respuesta.status_code == 403


def test_cliente_no_puede_modificar_estado(
    client,
    monkeypatch
):
    simular_auth(monkeypatch, CLIENTE)

    respuesta = client.put(
        "/orders/ord_inexistente/status",
        json={"status": "shipped"},
        headers=CABECERA
    )

    # Debe denegar el acceso antes de consultar el pedido.
    assert respuesta.status_code == 403


def test_admin_puede_acceder_a_operacion_protegida(
    client,
    monkeypatch
):
    simular_auth(monkeypatch, ADMIN)

    respuesta = client.put(
        "/orders/ord_inexistente/status",
        json={"status": "shipped"},
        headers=CABECERA
    )

    # El admin esta autorizado, pero el pedido no existe.
    assert respuesta.status_code == 404


def test_compra_con_usuario_diferente_rechazada(
    client,
    monkeypatch
):
    simular_auth(monkeypatch, CLIENTE)

    solicitud = {
        "user_id": "usr_otro_cliente",
        "items": [
            {
                "product_id": "prod_ejemplo",
                "size": "M",
                "quantity": 1,
                "unit_price": 25.0
            }
        ],
        "shipping_address": "Calle Mayor 12, Madrid"
    }

    respuesta = client.post(
        "/orders",
        json=solicitud,
        headers=CABECERA
    )

    assert respuesta.status_code == 403


def test_compra_consulta_usuario_en_auth(
    client,
    monkeypatch
):
    rutas_consultadas = []

    def responder(request):
        rutas_consultadas.append(request.url.path)

        if request.url.path == "/users/me":
            return httpx.Response(
                200,
                json=CLIENTE
            )

        if request.url.path == "/users/usr_cliente_test":
            return httpx.Response(
                200,
                json=CLIENTE
            )

        return httpx.Response(
            404,
            json={"detail": "No encontrado"}
        )

    transporte = httpx.MockTransport(responder)
    cliente_original = httpx.AsyncClient

    def cliente_simulado(*args, **kwargs):
        kwargs["transport"] = transporte
        return cliente_original(*args, **kwargs)

    monkeypatch.setattr(
        security_api.httpx,
        "AsyncClient",
        cliente_simulado
    )

    solicitud = {
        "user_id": CLIENTE["id"],
        "items": [
            {
                "product_id": "prod_inexistente",
                "size": "M",
                "quantity": 1,
                "unit_price": 25.0
            }
        ],
        "shipping_address": "Calle Mayor 12, Madrid"
    }

    respuesta = client.post(
        "/orders",
        json=solicitud,
        headers=CABECERA
    )

    # La autenticacion se ha completado.
    # Despues falla porque el producto no existe.
    assert respuesta.status_code == 400

    # Verificar la comunicacion exigida en OpenAPI.
    assert "/users/me" in rutas_consultadas
    assert "/users/usr_cliente_test" in rutas_consultadas
