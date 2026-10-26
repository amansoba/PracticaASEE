
import pytest

from openapi_server.models.extra_models import TokenModel
from openapi_server.security_api import get_admin_BearerAuth
from openapi_server.main import app


ARTISTA = {
    "name": "Daft Punk",
    "genre": "Electronica",
    "biography": "Duo frances de musica electronica",
    "image_url": "https://example.com/daftpunk.jpg"
}


@pytest.fixture
def administrador():
    # Simular administrador sin llamar a auth-service
    app.dependency_overrides[get_admin_BearerAuth] = (
        lambda: TokenModel(sub="usr_admin_test")
    )

    yield

    app.dependency_overrides.pop(
        get_admin_BearerAuth,
        None
    )


def crear_artista(client):
    respuesta = client.post(
        "/artists",
        json=ARTISTA
    )

    assert respuesta.status_code == 201
    return respuesta.json()


def test_listar_artistas_vacio(client):
    respuesta = client.get("/artists")

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_crear_artista(client, administrador):
    artista = crear_artista(client)

    assert artista["id"].startswith("art_")
    assert artista["name"] == "Daft Punk"
    assert artista["genre"] == "Electronica"


def test_obtener_artista_por_id(client, administrador):
    artista = crear_artista(client)

    respuesta = client.get(
        f"/artists/{artista['id']}"
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == artista["id"]


def test_artista_inexistente(client):
    respuesta = client.get(
        "/artists/art_no_existe"
    )

    assert respuesta.status_code == 404


def test_filtrar_artistas_por_genero(client, administrador):
    crear_artista(client)

    respuesta = client.get(
        "/artists",
        params={"genre": "electronica"}
    )

    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 1


def test_buscar_artista_por_nombre(client, administrador):
    crear_artista(client)

    respuesta = client.get(
        "/artists",
        params={"search": "daft"}
    )

    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 1


def test_actualizar_artista(client, administrador):
    artista = crear_artista(client)

    respuesta = client.put(
        f"/artists/{artista['id']}",
        json={
            "name": "Daft Punk",
            "genre": "House",
            "biography": "Biografia actualizada"
        }
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["genre"] == "House"


def test_eliminar_artista(client, administrador):
    artista = crear_artista(client)

    respuesta = client.delete(
        f"/artists/{artista['id']}"
    )

    assert respuesta.status_code == 204

    consulta = client.get(
        f"/artists/{artista['id']}"
    )

    assert consulta.status_code == 404


def test_crear_artista_sin_token(client):
    respuesta = client.post(
        "/artists",
        json=ARTISTA
    )

    assert respuesta.status_code == 401


def test_crear_artista_nombre_vacio(client, administrador):
    respuesta = client.post(
        "/artists",
        json={
            "name": "   ",
            "genre": "Electronica"
        }
    )

    assert respuesta.status_code == 400


def test_actualizar_artista_inexistente(client, administrador):
    respuesta = client.put(
        "/artists/art_no_existe",
        json=ARTISTA
    )

    assert respuesta.status_code == 404


def test_eliminar_artista_inexistente(client, administrador):
    respuesta = client.delete(
        "/artists/art_no_existe"
    )

    assert respuesta.status_code == 404
