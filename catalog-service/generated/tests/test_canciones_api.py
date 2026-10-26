
import pytest

from openapi_server.main import app
from openapi_server.models.extra_models import TokenModel
from openapi_server.security_api import get_admin_BearerAuth


@pytest.fixture
def administrador():
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
        json={
            "name": "Daft Punk",
            "genre": "Electronica"
        }
    )

    assert respuesta.status_code == 201

    return respuesta.json()


def crear_cancion(client, artista_id):
    respuesta = client.post(
        f"/artists/{artista_id}/songs",
        json={
            "title": "Get Lucky",
            "spotify_id": "2Foc5Q5nqNiosCNqttzNZB",
            "spotify_url": (
                "https://open.spotify.com/track/"
                "2Foc5Q5nqNiosCNqttzNZB"
            )
        }
    )

    return respuesta


def test_listar_canciones_vacio(client, administrador):
    artista = crear_artista(client)

    respuesta = client.get(
        f"/artists/{artista['id']}/songs"
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_anadir_cancion(client, administrador):
    artista = crear_artista(client)

    respuesta = crear_cancion(
        client,
        artista["id"]
    )

    assert respuesta.status_code == 201

    cancion = respuesta.json()

    assert cancion["id"].startswith("song_")
    assert cancion["artist_id"] == artista["id"]
    assert cancion["title"] == "Get Lucky"


def test_listar_canciones(client, administrador):
    artista = crear_artista(client)

    crear_cancion(client, artista["id"])

    respuesta = client.get(
        f"/artists/{artista['id']}/songs"
    )

    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 1


def test_canciones_artista_inexistente(client):
    respuesta = client.get(
        "/artists/art_no_existe/songs"
    )

    assert respuesta.status_code == 404


def test_anadir_cancion_artista_inexistente(
    client,
    administrador
):
    respuesta = client.post(
        "/artists/art_no_existe/songs",
        json={
            "title": "Cancion de prueba"
        }
    )

    assert respuesta.status_code == 404


def test_anadir_cancion_titulo_vacio(
    client,
    administrador
):
    artista = crear_artista(client)

    respuesta = client.post(
        f"/artists/{artista['id']}/songs",
        json={
            "title": "   "
        }
    )

    assert respuesta.status_code == 400


def test_anadir_cancion_sin_token(client):
    respuesta = client.post(
        "/artists/art_no_existe/songs",
        json={
            "title": "Cancion"
        }
    )

    assert respuesta.status_code == 401


def test_borrar_artista_elimina_canciones(
    client,
    administrador
):
    artista = crear_artista(client)

    crear_cancion(client, artista["id"])

    borrado = client.delete(
        f"/artists/{artista['id']}"
    )

    assert borrado.status_code == 204

    consulta = client.get(
        f"/artists/{artista['id']}/songs"
    )

    assert consulta.status_code == 404


def test_cancion_sin_credenciales_spotify(
    client,
    administrador,
    monkeypatch
):
    # Sin credenciales, guardamos los datos recibidos.
    monkeypatch.setattr(
        "openapi_server.impl.canciones_impl.spotify_configurado",
        lambda: False
    )

    artista = crear_artista(client)

    respuesta = crear_cancion(
        client,
        artista["id"]
    )

    assert respuesta.status_code == 201

    cancion = respuesta.json()

    assert cancion["title"] == "Get Lucky"
    assert cancion["spotify_id"] == (
        "2Foc5Q5nqNiosCNqttzNZB"
    )


def test_cancion_con_metadatos_spotify(
    client,
    administrador,
    monkeypatch
):
    # Simular que Spotify esta configurado.
    monkeypatch.setattr(
        "openapi_server.impl.canciones_impl.spotify_configurado",
        lambda: True
    )

    async def simular_spotify(spotify_id):
        return {
            "spotify_id": spotify_id,
            "title": "Get Lucky - Spotify",
            "spotify_url": (
                "https://open.spotify.com/track/"
                + spotify_id
            ),
            "preview_url": None,
            "artists": ["Daft Punk"]
        }

    monkeypatch.setattr(
        "openapi_server.impl.canciones_impl.obtener_cancion_spotify",
        simular_spotify
    )

    artista = crear_artista(client)

    respuesta = crear_cancion(
        client,
        artista["id"]
    )

    assert respuesta.status_code == 201

    cancion = respuesta.json()

    assert cancion["title"] == "Get Lucky - Spotify"
    assert cancion["spotify_id"] == (
        "2Foc5Q5nqNiosCNqttzNZB"
    )
    assert cancion["preview_url"] is None


def test_error_spotify_no_guarda_cancion(
    client,
    administrador,
    monkeypatch
):
    from fastapi import HTTPException

    monkeypatch.setattr(
        "openapi_server.impl.canciones_impl.spotify_configurado",
        lambda: True
    )

    async def simular_error(spotify_id):
        raise HTTPException(
            status_code=503,
            detail="Spotify no disponible"
        )

    monkeypatch.setattr(
        "openapi_server.impl.canciones_impl.obtener_cancion_spotify",
        simular_error
    )

    artista = crear_artista(client)

    respuesta = crear_cancion(
        client,
        artista["id"]
    )

    assert respuesta.status_code == 503

    # Comprobar que no se ha guardado nada.
    canciones = client.get(
        f"/artists/{artista['id']}/songs"
    )

    assert canciones.status_code == 200
    assert canciones.json() == []
