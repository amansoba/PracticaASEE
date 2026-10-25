
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import select

from openapi_server.database import SessionLocal
from openapi_server.db_models import EventDB


# Token provisional para pruebas locales
HEADERS = {
    "Authorization": "Bearer dev-test-only"
}


# Datos utilizados para crear festivales de prueba
DATOS_EVENTO = {
    "name": "Subsonic Festival Test",
    "start_date": "2027-07-20",
    "end_date": "2027-07-22",
    "venue": "Recinto de Pruebas",
    "location_city": "Madrid"
}


@pytest.fixture
def eventos_prueba():
    # Guardar los identificadores creados durante cada test
    ids_creados = []

    yield ids_creados

    # Eliminar exclusivamente los eventos creados por este test
    with SessionLocal() as db:
        for evento_id in ids_creados:
            evento = db.get(EventDB, evento_id)

            if evento is not None:
                db.delete(evento)

        db.commit()


def crear_evento(client: TestClient, eventos_prueba):
    # Crear un festival y registrar su ID para limpiarlo despues
    response = client.post(
        "/events",
        json=DATOS_EVENTO,
        headers=HEADERS
    )

    assert response.status_code == 201

    evento = response.json()
    eventos_prueba.append(evento["id"])

    return evento


# TEST 1: GET /events
def test_get_all_events(client: TestClient):

    response = client.get("/events")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# TEST 2: POST /events
def test_create_event(
    client: TestClient,
    eventos_prueba
):

    evento = crear_evento(client, eventos_prueba)

    assert evento["name"] == DATOS_EVENTO["name"]
    assert evento["venue"] == DATOS_EVENTO["venue"]
    assert evento["location_city"] == DATOS_EVENTO["location_city"]
    assert evento["id"].startswith("evt_")


# TEST 3: GET /events/{id}
def test_get_event_by_id(
    client: TestClient,
    eventos_prueba
):

    evento = crear_evento(client, eventos_prueba)

    response = client.get(
        f"/events/{evento['id']}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == evento["id"]
    assert response.json()["name"] == evento["name"]


# TEST 4: PUT /events/{id}
def test_update_event(
    client: TestClient,
    eventos_prueba
):

    evento = crear_evento(client, eventos_prueba)

    datos_actualizados = {
        "name": "Subsonic Festival Actualizado",
        "start_date": "2027-07-20",
        "end_date": "2027-07-23",
        "venue": "Nuevo Recinto",
        "location_city": "Barcelona"
    }

    response = client.put(
        f"/events/{evento['id']}",
        json=datos_actualizados,
        headers=HEADERS
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Subsonic Festival Actualizado"
    assert response.json()["location_city"] == "Barcelona"
    assert response.json()["end_date"] == "2027-07-23"


# TEST 5: DELETE /events/{id}
def test_delete_event(
    client: TestClient,
    eventos_prueba
):

    evento = crear_evento(client, eventos_prueba)

    response = client.delete(
        f"/events/{evento['id']}",
        headers=HEADERS
    )

    assert response.status_code == 204
    assert response.content == b""

    # Comprobar que el evento ya no existe
    response_get = client.get(
        f"/events/{evento['id']}"
    )

    assert response_get.status_code == 404
