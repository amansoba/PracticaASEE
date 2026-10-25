# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field  # noqa: F401
from typing import Any, List  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from openapi_server.models.create_schedule_entry_request import CreateScheduleEntryRequest  # noqa: F401
from openapi_server.models.schedule_entry import ScheduleEntry  # noqa: F401


def test_get_event_lineup(client: TestClient):
    """Test case for get_event_lineup

    Obtener el cartel (Line-up) y horarios del festival
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/events/{id}/lineup".format(id='evt_101'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_add_schedule_entry(client: TestClient):
    """Test case for add_schedule_entry

    Añadir una actuación al line-up del evento
    """
    create_schedule_entry_request = openapi_server.CreateScheduleEntryRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/events/{id}/lineup".format(id='evt_101'),
    #    headers=headers,
    #    json=create_schedule_entry_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

