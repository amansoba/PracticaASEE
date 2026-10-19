# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field  # noqa: F401
from typing import Any, List  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from openapi_server.models.create_song_request import CreateSongRequest  # noqa: F401
from openapi_server.models.song import Song  # noqa: F401


def test_get_songs_by_artist(client: TestClient):
    """Test case for get_songs_by_artist

    Listar canciones de un artista
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/artists/{id}/songs".format(id='art_12345'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_add_song_to_artist(client: TestClient):
    """Test case for add_song_to_artist

    Añadir una canción al repertorio de un artista
    """
    create_song_request = openapi_server.CreateSongRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/artists/{id}/songs".format(id='art_12345'),
    #    headers=headers,
    #    json=create_song_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

