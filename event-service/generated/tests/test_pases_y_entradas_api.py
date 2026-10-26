
import httpx
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import delete

from openapi_server.database import SessionLocal
from openapi_server.db_models import (
    EventDB,
    PassConfigDB,
    TicketDB
)


HEADERS = {
    "Authorization": "Bearer dev-test-only"
}

DATOS_EVENTO = {
    "name": "Subsonic Festival Test Entradas",
    "start_date": "2027-08-10",
    "end_date": "2027-08-12",
    "venue": "Recinto de Pruebas",
    "location_city": "Caceres"
}

DATOS_PASE = {
    "type_name": "Abono General",
    "price": 120.0,
    "capacity": 2,
    "benefits": ["Acceso general"]
}

USUARIO_PRUEBA = "usr_test_555"


@pytest.fixture
def festival_prueba(client: TestClient):

    response = client.post(
        "/events",
        json=DATOS_EVENTO,
        headers=HEADERS
    )

    assert response.status_code == 201

    evento_id = response.json()["id"]

    yield evento_id

    # Borrar solamente los datos relacionados con este
    # festival de prueba, respetando las claves foraneas.
    with SessionLocal() as db:

        db.execute(
            delete(TicketDB).where(
                TicketDB.event_id == evento_id
            )
        )

        db.execute(
            delete(PassConfigDB).where(
                PassConfigDB.event_id == evento_id
            )
        )

        db.execute(
            delete(EventDB).where(
                EventDB.id == evento_id
            )
        )

        db.commit()


@pytest.fixture
def autenticacion_simulada(monkeypatch):

    # Simular auth-service exclusivamente durante el test.
    class ClienteAutenticacionFalso:

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, **kwargs):

            if url.endswith(f"/users/{USUARIO_PRUEBA}"):
                return httpx.Response(
                    status_code=200,
                    json={
                        "id": USUARIO_PRUEBA,
                        "name": "Usuario de Prueba"
                    }
                )

            return httpx.Response(
                status_code=404,
                json={"detail": "Usuario no encontrado"}
            )

    monkeypatch.setenv(
        "AUTH_SERVICE_URL",
        "http://auth-service-test"
    )

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: ClienteAutenticacionFalso()
    )


def crear_pase(
    client: TestClient,
    evento_id: str,
    capacity: int = 2
):

    datos = DATOS_PASE.copy()
    datos["capacity"] = capacity

    response = client.post(
        f"/events/{evento_id}/passes",
        json=datos,
        headers=HEADERS
    )

    assert response.status_code == 201

    return response.json()


def comprar_entrada(
    client: TestClient,
    evento_id: str,
    pase_id: str,
    usuario_id: str = USUARIO_PRUEBA
):

    return client.post(
        "/tickets/purchase",
        json={
            "event_id": evento_id,
            "pass_id": pase_id,
            "user_id": usuario_id,
            "payment_token": "tok_test_only"
        },
        headers=HEADERS
    )


# TEST 1: GET /events/{id}/passes
def test_get_pass_configs_by_event(
    client: TestClient,
    festival_prueba
):

    response = client.get(
        f"/events/{festival_prueba}/passes"
    )

    assert response.status_code == 200
    assert response.json() == []


# TEST 2: POST /events/{id}/passes
def test_create_pass_config(
    client: TestClient,
    festival_prueba
):

    pase = crear_pase(client, festival_prueba)

    assert pase["id"].startswith("pass_")
    assert pase["event_id"] == festival_prueba
    assert pase["type_name"] == "Abono General"
    assert float(pase["price"]) == 120.0
    assert pase["capacity"] == 2
    assert pase["available_tickets"] == 2

    # Comprobar que el pase esta guardado.
    response = client.get(
        f"/events/{festival_prueba}/passes"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == pase["id"]


# TEST 3: POST /tickets/purchase
def test_purchase_ticket(
    client: TestClient,
    festival_prueba,
    autenticacion_simulada
):

    pase = crear_pase(client, festival_prueba)

    response = comprar_entrada(
        client,
        festival_prueba,
        pase["id"]
    )

    assert response.status_code == 201

    entrada = response.json()

    assert entrada["id"].startswith("tck_")
    assert entrada["event_id"] == festival_prueba
    assert entrada["pass_id"] == pase["id"]
    assert entrada["user_id"] == USUARIO_PRUEBA
    assert entrada["status"] == "valid"
    assert entrada["qr_code"].startswith("SUBSONIC-")

    # Comprobar que el aforo se ha descontado.
    response_pases = client.get(
        f"/events/{festival_prueba}/passes"
    )

    assert response_pases.status_code == 200
    assert response_pases.json()[0]["available_tickets"] == 1


# TEST 4: GET /tickets/user/{userId}
def test_get_tickets_by_user(
    client: TestClient,
    festival_prueba,
    autenticacion_simulada
):

    pase = crear_pase(client, festival_prueba)

    compra = comprar_entrada(
        client,
        festival_prueba,
        pase["id"]
    )

    assert compra.status_code == 201

    entrada_id = compra.json()["id"]

    response = client.get(
        f"/tickets/user/{USUARIO_PRUEBA}",
        headers=HEADERS
    )

    assert response.status_code == 200

    entradas = response.json()

    assert any(
        entrada["id"] == entrada_id
        for entrada in entradas
    )


# TEST 5: No superar el aforo
def test_aforo_agotado(
    client: TestClient,
    festival_prueba,
    autenticacion_simulada
):

    pase = crear_pase(
        client,
        festival_prueba,
        capacity=1
    )

    primera = comprar_entrada(
        client,
        festival_prueba,
        pase["id"]
    )

    assert primera.status_code == 201

    segunda = comprar_entrada(
        client,
        festival_prueba,
        pase["id"]
    )

    assert segunda.status_code == 409

    # Verificar que el aforo no es negativo.
    response = client.get(
        f"/events/{festival_prueba}/passes"
    )

    assert response.status_code == 200
    assert response.json()[0]["available_tickets"] == 0


# TEST 6: Rechazar un pase con datos invalidos
def test_create_pass_config_invalido(
    client: TestClient,
    festival_prueba
):

    datos = DATOS_PASE.copy()
    datos["price"] = -10

    response = client.post(
        f"/events/{festival_prueba}/passes",
        json=datos,
        headers=HEADERS
    )

    assert response.status_code == 400

    datos["price"] = 100
    datos["capacity"] = 0

    response = client.post(
        f"/events/{festival_prueba}/passes",
        json=datos,
        headers=HEADERS
    )

    assert response.status_code == 400


# TEST 7: Rechazar la compra sin auth-service
def test_autenticacion_no_disponible(
    client: TestClient,
    festival_prueba,
    monkeypatch
):

    pase = crear_pase(client, festival_prueba)

    monkeypatch.delenv(
        "AUTH_SERVICE_URL",
        raising=False
    )

    response = comprar_entrada(
        client,
        festival_prueba,
        pase["id"]
    )

    assert response.status_code == 503

    # Comprobar que no se ha descontado el aforo.
    response_pases = client.get(
        f"/events/{festival_prueba}/passes"
    )

    assert response_pases.status_code == 200
    assert response_pases.json()[0]["available_tickets"] == 2


# TEST 8: Impedir compras a nombre de otro usuario
def test_usuario_inexistente(
    client: TestClient,
    festival_prueba,
    autenticacion_simulada
):

    pase = crear_pase(client, festival_prueba)

    # El usuario autenticado es usr_test_555,
    # pero intenta comprar para otro usuario.
    response = comprar_entrada(
        client,
        festival_prueba,
        pase["id"],
        usuario_id="usr_inexistente"
    )

    # La seguridad debe impedir la operacion.
    assert response.status_code == 403

    # Comprobar que el aforo no se ha modificado.
    response_pases = client.get(
        f"/events/{festival_prueba}/passes"
    )

    assert response_pases.status_code == 200
    assert response_pases.json()[0]["available_tickets"] == 2
