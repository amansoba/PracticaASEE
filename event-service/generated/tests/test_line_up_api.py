
import pytest
import httpx

from fastapi.testclient import TestClient
from sqlalchemy import select, delete

from openapi_server.database import SessionLocal
from openapi_server.db_models import EventDB, ScheduleEntryDB


# Token provisional utilizado durante las pruebas
HEADERS = {
    "Authorization": "Bearer dev-test-only"
}


# Festival utilizado en las pruebas
DATOS_EVENTO = {
    "name": "Subsonic Festival Test Line-up",
    "start_date": "2027-07-20",
    "end_date": "2027-07-22",
    "venue": "Recinto de Pruebas",
    "location_city": "Madrid"
}


# Actuacion de prueba
DATOS_ACTUACION = {
    "artist_id": "art_12345",
    "artist_name": "Daft Punk",
    "stage": "Main Stage",
    "start_time": "2027-07-20T22:00:00Z",
    "end_time": "2027-07-20T23:30:00Z"
}


@pytest.fixture
def festival_prueba(client: TestClient):

    # Crear un festival para cada test
    response = client.post(
        "/events",
        json=DATOS_EVENTO,
        headers=HEADERS
    )

    assert response.status_code == 201

    evento_id = response.json()["id"]

    yield evento_id

    # Limpiar los datos creados para este festival
    with SessionLocal() as db:

        # Primero eliminar las actuaciones asociadas
        db.execute(
            delete(ScheduleEntryDB).where(
                ScheduleEntryDB.event_id == evento_id
            )
        )

        # Despues eliminar el festival
        db.execute(
            delete(EventDB).where(
                EventDB.id == evento_id
            )
        )

        db.commit()



@pytest.fixture
def catalogo_simulado(monkeypatch):

    # Simular exclusivamente la respuesta de catalog-service
    class ClienteCatalogoFalso:

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url):
            return httpx.Response(
                status_code=200,
                json={
                    "id": "art_12345",
                    "name": "Daft Punk"
                }
            )

    monkeypatch.setenv(
        "CATALOG_SERVICE_URL",
        "http://catalogo-test"
    )

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: ClienteCatalogoFalso()
    )


# TEST 1: Consultar un Line-up vacio
def test_get_event_lineup(
    client: TestClient,
    festival_prueba
):

    response = client.get(
        f"/events/{festival_prueba}/lineup"
    )

    assert response.status_code == 200
    assert response.json() == []


# TEST 2: Añadir una actuacion al Line-up
def test_add_schedule_entry(
    client: TestClient,
    festival_prueba,
    catalogo_simulado
):

    response = client.post(
        f"/events/{festival_prueba}/lineup",
        json=DATOS_ACTUACION,
        headers=HEADERS
    )

    assert response.status_code == 201

    actuacion = response.json()

    assert actuacion["artist_id"] == "art_12345"
    assert actuacion["artist_name"] == "Daft Punk"
    assert actuacion["stage"] == "Main Stage"
    assert actuacion["id"].startswith("sch_")

    # Comprobar que se ha guardado en PostgreSQL
    with SessionLocal() as db:

        actuacion_db = db.get(
            ScheduleEntryDB,
            actuacion["id"]
        )

        assert actuacion_db is not None
        assert actuacion_db.event_id == festival_prueba

    # Comprobar que GET recupera la actuacion
    response_get = client.get(
        f"/events/{festival_prueba}/lineup"
    )

    assert response_get.status_code == 200
    assert len(response_get.json()) == 1
    assert response_get.json()[0]["id"] == actuacion["id"]


# TEST 3: Rechazar actuaciones con fechas incorrectas
def test_fechas_incorrectas(
    client: TestClient,
    festival_prueba
):

    datos = DATOS_ACTUACION.copy()

    datos["start_time"] = "2027-07-20T23:30:00Z"
    datos["end_time"] = "2027-07-20T22:00:00Z"

    response = client.post(
        f"/events/{festival_prueba}/lineup",
        json=datos,
        headers=HEADERS
    )

    assert response.status_code == 400


# TEST 4: Rechazar solapamientos en el mismo escenario
def test_solapamiento_horario(
    client: TestClient,
    festival_prueba,
    catalogo_simulado
):

    # Registrar la primera actuacion
    primera = client.post(
        f"/events/{festival_prueba}/lineup",
        json=DATOS_ACTUACION,
        headers=HEADERS
    )

    assert primera.status_code == 201

    # Intentar registrar otra actuacion superpuesta
    datos = DATOS_ACTUACION.copy()

    datos["artist_id"] = "art_67890"
    datos["artist_name"] = "Otro Artista"
    datos["start_time"] = "2027-07-20T23:00:00Z"
    datos["end_time"] = "2027-07-21T00:30:00Z"

    response = client.post(
        f"/events/{festival_prueba}/lineup",
        json=datos,
        headers=HEADERS
    )

    assert response.status_code == 400

    # La segunda actuacion no debe guardarse
    response_get = client.get(
        f"/events/{festival_prueba}/lineup"
    )

    assert len(response_get.json()) == 1


# TEST 5: Festival inexistente
def test_lineup_evento_inexistente(
    client: TestClient
):

    response = client.get(
        "/events/evt_no_existe/lineup"
    )

    assert response.status_code == 404


# TEST 6: Catalogo no disponible
def test_catalogo_no_disponible(
    client: TestClient,
    festival_prueba,
    monkeypatch
):

    monkeypatch.delenv(
        "CATALOG_SERVICE_URL",
        raising=False
    )

    response = client.post(
        f"/events/{festival_prueba}/lineup",
        json=DATOS_ACTUACION,
        headers=HEADERS
    )

    assert response.status_code == 503

    # Comprobar que no se ha guardado nada
    with SessionLocal() as db:

        actuaciones = db.scalars(
            select(ScheduleEntryDB)
            .where(
                ScheduleEntryDB.event_id == festival_prueba
            )
        ).all()

        assert len(actuaciones) == 0
