
import httpx
import pytest

from fastapi.testclient import TestClient

from openapi_server.main import app
from openapi_server.security_api import get_token_BearerAuth


HEADERS = {
    "Authorization": "Bearer token_de_prueba"
}

DATOS_EVENTO = {
    "name": "Festival de Seguridad",
    "start_date": "2027-07-20",
    "end_date": "2027-07-22",
    "venue": "Recinto de Pruebas",
    "location_city": "Caceres"
}


@pytest.fixture
def cliente_seguridad(monkeypatch):

    # Activar la seguridad real de nuestro microservicio.
    # No se utiliza la identidad simulada de conftest.py.
    app.dependency_overrides.pop(
        get_token_BearerAuth,
        None
    )

    monkeypatch.setenv(
        "AUTH_SERVICE_URL",
        "http://auth-service-test"
    )

    with TestClient(app) as cliente:
        yield cliente


def simular_usuario(monkeypatch, usuario_id, rol):

    # Simular la respuesta de GET /users/me.
    class ClienteAutenticacionFalso:

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, **kwargs):
            return httpx.Response(
                status_code=200,
                json={
                    "id": usuario_id,
                    "name": "Usuario de Prueba",
                    "email": "test@example.com",
                    "role": rol
                }
            )

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: ClienteAutenticacionFalso()
    )


# TEST 1: No permitir operaciones sin token
def test_sin_token(cliente_seguridad):

    response = cliente_seguridad.post(
        "/events",
        json=DATOS_EVENTO
    )

    assert response.status_code == 401


# TEST 2: Rechazar tokens invalidos
def test_token_invalido(
    cliente_seguridad,
    monkeypatch
):

    class ClienteAutenticacionFalso:

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, **kwargs):
            return httpx.Response(
                status_code=401
            )

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: ClienteAutenticacionFalso()
    )

    response = cliente_seguridad.post(
        "/events",
        json=DATOS_EVENTO,
        headers=HEADERS
    )

    assert response.status_code == 401


# TEST 3: Un cliente no puede crear festivales
def test_cliente_no_es_administrador(
    cliente_seguridad,
    monkeypatch
):

    simular_usuario(
        monkeypatch,
        "usr_555",
        "client"
    )

    response = cliente_seguridad.post(
        "/events",
        json=DATOS_EVENTO,
        headers=HEADERS
    )

    assert response.status_code == 403


# TEST 4: Un administrador puede superar
# la comprobacion de seguridad
def test_administrador_autorizado(
    cliente_seguridad,
    monkeypatch
):

    simular_usuario(
        monkeypatch,
        "usr_admin",
        "admin"
    )

    response = cliente_seguridad.post(
        "/events",
        json=DATOS_EVENTO,
        headers=HEADERS
    )

    # La autenticacion y autorizacion deben permitirlo.
    assert response.status_code == 201

    # Limpiar el festival creado durante el test.
    evento_id = response.json()["id"]

    eliminacion = cliente_seguridad.delete(
        f"/events/{evento_id}",
        headers=HEADERS
    )

    assert eliminacion.status_code == 204


# TEST 5: Un usuario no puede consultar
# las entradas de otro usuario
def test_consulta_entradas_ajenas(
    cliente_seguridad,
    monkeypatch
):

    simular_usuario(
        monkeypatch,
        "usr_555",
        "client"
    )

    response = cliente_seguridad.get(
        "/tickets/user/usr_999",
        headers=HEADERS
    )

    assert response.status_code == 403


# TEST 6: Un usuario puede consultar
# sus propias entradas
def test_consulta_entradas_propias(
    cliente_seguridad,
    monkeypatch
):

    simular_usuario(
        monkeypatch,
        "usr_555",
        "client"
    )

    response = cliente_seguridad.get(
        "/tickets/user/usr_555",
        headers=HEADERS
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# TEST 7: Un usuario no puede comprar
# entradas a nombre de otra persona
def test_compra_para_otro_usuario(
    cliente_seguridad,
    monkeypatch
):

    simular_usuario(
        monkeypatch,
        "usr_555",
        "client"
    )

    response = cliente_seguridad.post(
        "/tickets/purchase",
        json={
            "event_id": "evt_prueba",
            "pass_id": "pass_prueba",
            "user_id": "usr_999"
        },
        headers=HEADERS
    )

    assert response.status_code == 403


# TEST 8: No permitir operaciones protegidas
# si auth-service no esta configurado
def test_autenticacion_no_configurada(
    cliente_seguridad,
    monkeypatch
):

    monkeypatch.delenv(
        "AUTH_SERVICE_URL",
        raising=False
    )

    response = cliente_seguridad.post(
        "/events",
        json=DATOS_EVENTO,
        headers=HEADERS
    )

    assert response.status_code == 503
