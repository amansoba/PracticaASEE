
import pytest

from openapi_server.main import app
from openapi_server.models.extra_models import TokenModel
from openapi_server.security_api import get_admin_BearerAuth


@pytest.fixture
def administrador():

    app.dependency_overrides[
        get_admin_BearerAuth
    ] = lambda: TokenModel(sub="usr_admin_test")

    yield

    app.dependency_overrides.pop(
        get_admin_BearerAuth,
        None
    )


def crear_artista(client, nombre="Artista Prueba"):

    respuesta = client.post(
        "/artists",
        json={
            "name": nombre,
            "genre": "Electronica"
        }
    )

    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def crear_cancion(client, artista_id):

    respuesta = client.post(
        f"/artists/{artista_id}/songs",
        json={
            "title": "Cancion Original"
        }
    )

    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def ruta_cancion(artista_id, cancion_id):
    return (
        f"/artists/{artista_id}/songs/{cancion_id}"
    )


# ============================================================
# TEST 1 - ACTUALIZAR CANCION
# ============================================================

def test_actualizar_cancion(client, administrador):

    artista = crear_artista(client)
    cancion = crear_cancion(client, artista["id"])

    respuesta = client.put(
        ruta_cancion(artista["id"], cancion["id"]),
        json={
            "title": "Cancion Actualizada",
            "spotify_id": "spotify123"
        }
    )

    assert respuesta.status_code == 200, respuesta.text

    datos = respuesta.json()

    assert datos["id"] == cancion["id"]
    assert datos["title"] == "Cancion Actualizada"
    assert datos["spotify_id"] == "spotify123"

    listado = client.get(
        f"/artists/{artista['id']}/songs"
    )

    assert listado.status_code == 200
    assert listado.json()[0]["title"] == "Cancion Actualizada"


# ============================================================
# TEST 2 - ELIMINAR CANCION
# ============================================================

def test_eliminar_cancion(client, administrador):

    artista = crear_artista(client)
    cancion = crear_cancion(client, artista["id"])

    respuesta = client.delete(
        ruta_cancion(artista["id"], cancion["id"])
    )

    assert respuesta.status_code == 204

    listado = client.get(
        f"/artists/{artista['id']}/songs"
    )

    assert listado.status_code == 200
    assert listado.json() == []


# ============================================================
# TEST 3 - CANCION INEXISTENTE
# ============================================================

def test_cancion_inexistente(client, administrador):

    artista = crear_artista(client)

    respuesta = client.put(
        ruta_cancion(artista["id"], "song_inexistente"),
        json={"title": "Nueva Cancion"}
    )

    assert respuesta.status_code == 404


# ============================================================
# TEST 4 - TITULO VACIO
# ============================================================

def test_actualizar_titulo_vacio(client, administrador):

    artista = crear_artista(client)
    cancion = crear_cancion(client, artista["id"])

    respuesta = client.put(
        ruta_cancion(artista["id"], cancion["id"]),
        json={"title": "   "}
    )

    assert respuesta.status_code == 400


# ============================================================
# TEST 5 - IMPEDIR OPERACION SIN TOKEN
# ============================================================

def test_editar_cancion_sin_token(client):

    respuesta = client.put(
        "/artists/art_prueba/songs/song_prueba",
        json={"title": "Cancion"}
    )

    assert respuesta.status_code == 401


# ============================================================
# TEST 6 - NO EDITAR CANCION DE OTRO ARTISTA
# ============================================================

def test_cancion_de_otro_artista(client, administrador):

    artista_1 = crear_artista(client, "Artista Uno")
    artista_2 = crear_artista(client, "Artista Dos")

    cancion = crear_cancion(client, artista_1["id"])

    respuesta = client.delete(
        ruta_cancion(artista_2["id"], cancion["id"])
    )

    assert respuesta.status_code == 404

    listado = client.get(
        f"/artists/{artista_1['id']}/songs"
    )

    assert listado.status_code == 200
    assert len(listado.json()) == 1
