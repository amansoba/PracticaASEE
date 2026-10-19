# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field  # noqa: F401
from typing import Any, List, Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from openapi_server.models.artist import Artist  # noqa: F401
from openapi_server.models.create_artist_request import CreateArtistRequest  # noqa: F401


def test_get_artists(client: TestClient):
    """Test case for get_artists

    Consultar lista de artistas
    """
    params = [("genre", 'Electrónica'),     ("search", 'Daft')]
    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/artists",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_create_artist(client: TestClient):
    """Test case for create_artist

    Crear un nuevo artista
    """
    create_artist_request = openapi_server.CreateArtistRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/artists",
    #    headers=headers,
    #    json=create_artist_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_artist_by_id(client: TestClient):
    """Test case for get_artist_by_id

    Obtener el detalle de un artista
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/artists/{id}".format(id='art_12345'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_update_artist(client: TestClient):
    """Test case for update_artist

    Actualizar ficha de un artista
    """
    create_artist_request = openapi_server.CreateArtistRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PUT",
    #    "/artists/{id}".format(id='art_12345'),
    #    headers=headers,
    #    json=create_artist_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_delete_artist(client: TestClient):
    """Test case for delete_artist

    Eliminar un artista del catálogo
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/artists/{id}".format(id='art_12345'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

