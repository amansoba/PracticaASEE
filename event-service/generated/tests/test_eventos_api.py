# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field  # noqa: F401
from typing import Any, List  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from openapi_server.models.create_event_request import CreateEventRequest  # noqa: F401
from openapi_server.models.event import Event  # noqa: F401


def test_get_all_events(client: TestClient):
    """Test case for get_all_events

    Listar todos los festivales y eventos
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/events",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_create_event(client: TestClient):
    """Test case for create_event

    Crear un nuevo evento o edición
    """
    create_event_request = openapi_server.CreateEventRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/events",
    #    headers=headers,
    #    json=create_event_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_event_by_id(client: TestClient):
    """Test case for get_event_by_id

    Consultar detalles de un evento
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/events/{id}".format(id='evt_101'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_update_event(client: TestClient):
    """Test case for update_event

    Actualizar información de un evento
    """
    create_event_request = openapi_server.CreateEventRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PUT",
    #    "/events/{id}".format(id='evt_101'),
    #    headers=headers,
    #    json=create_event_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_delete_event(client: TestClient):
    """Test case for delete_event

    Cancelar o eliminar un evento
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/events/{id}".format(id='evt_101'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

