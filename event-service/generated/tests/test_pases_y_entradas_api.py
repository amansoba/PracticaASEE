# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field  # noqa: F401
from typing import Any, List  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from openapi_server.models.create_pass_config_request import CreatePassConfigRequest  # noqa: F401
from openapi_server.models.pass_config import PassConfig  # noqa: F401
from openapi_server.models.ticket import Ticket  # noqa: F401
from openapi_server.models.ticket_purchase_request import TicketPurchaseRequest  # noqa: F401


def test_get_pass_configs_by_event(client: TestClient):
    """Test case for get_pass_configs_by_event

    Consultar los tipos de pases y aforo configurado
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/events/{id}/passes".format(id='evt_101'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_create_pass_config(client: TestClient):
    """Test case for create_pass_config

    Configurar un nuevo tipo de pase para el evento
    """
    create_pass_config_request = openapi_server.CreatePassConfigRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/events/{id}/passes".format(id='evt_101'),
    #    headers=headers,
    #    json=create_pass_config_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_purchase_ticket(client: TestClient):
    """Test case for purchase_ticket

    Comprar una entrada / pase para un evento
    """
    ticket_purchase_request = openapi_server.TicketPurchaseRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/tickets/purchase",
    #    headers=headers,
    #    json=ticket_purchase_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_tickets_by_user(client: TestClient):
    """Test case for get_tickets_by_user

    Consultar las entradas adquiridas por un usuario
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/tickets/user/{userId}".format(userId='usr_555'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

