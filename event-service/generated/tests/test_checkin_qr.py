
from datetime import date, datetime, timezone
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import delete

from openapi_server.database import SessionLocal
from openapi_server.db_models import (
    EventDB,
    PassConfigDB,
    TicketDB
)
from openapi_server.security_api import get_token_BearerAuth


HEADERS = {
    "Authorization": "Bearer token_de_prueba"
}


# ============================================================
# CREAR ENTRADA DE PRUEBA
# ============================================================

@pytest.fixture
def entrada_prueba():

    identificador = uuid4().hex

    evento_id = f"evt_qr_{identificador}"
    pase_id = f"pass_qr_{identificador}"
    entrada_id = f"tck_qr_{identificador}"
    codigo_qr = f"SUBSONIC-{identificador}"

    with SessionLocal() as db:

        db.add(
            EventDB(
                id=evento_id,
                name="Festival QR Test",
                start_date=date(2027, 8, 10),
                end_date=date(2027, 8, 12),
                venue="Recinto Test",
                location_city="Caceres"
            )
        )

        db.flush()

        db.add(
            PassConfigDB(
                id=pase_id,
                event_id=evento_id,
                type_name="General",
                price=50,
                capacity=2,
                available_tickets=1,
                benefits=[]
            )
        )

        db.flush()

        db.add(
            TicketDB(
                id=entrada_id,
                event_id=evento_id,
                pass_id=pase_id,
                user_id="usr_test_555",
                qr_code=codigo_qr,
                status="valid",
                purchased_at=datetime.now(timezone.utc)
            )
        )

        db.commit()

    yield {
        "id": entrada_id,
        "qr_code": codigo_qr
    }

    # Eliminar los datos creados por la prueba.
    with SessionLocal() as db:

        db.execute(
            delete(TicketDB).where(
                TicketDB.id == entrada_id
            )
        )

        db.execute(
            delete(PassConfigDB).where(
                PassConfigDB.id == pase_id
            )
        )

        db.execute(
            delete(EventDB).where(
                EventDB.id == evento_id
            )
        )

        db.commit()


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def consultar_estado(entrada_id):

    with SessionLocal() as db:
        entrada = db.get(TicketDB, entrada_id)

        assert entrada is not None

        return entrada.status


def validar(client, codigo):

    return client.post(
        "/tickets/validate",
        json={"qr_code": codigo},
        headers=HEADERS
    )


# ============================================================
# TEST 1 - CHECK-IN CORRECTO
# ============================================================

def test_checkin_qr_correcto(
    client,
    entrada_prueba
):

    respuesta = validar(
        client,
        entrada_prueba["qr_code"]
    )

    assert respuesta.status_code == 200, respuesta.text

    assert respuesta.json()["id"] == entrada_prueba["id"]
    assert respuesta.json()["status"] == "used"

    assert consultar_estado(
        entrada_prueba["id"]
    ) == "used"


# ============================================================
# TEST 2 - NO PERMITIR DOBLE CHECK-IN
# ============================================================

def test_checkin_qr_no_puede_repetirse(
    client,
    entrada_prueba
):

    primera = validar(
        client,
        entrada_prueba["qr_code"]
    )

    segunda = validar(
        client,
        entrada_prueba["qr_code"]
    )

    assert primera.status_code == 200
    assert segunda.status_code == 409

    assert consultar_estado(
        entrada_prueba["id"]
    ) == "used"


# ============================================================
# TEST 3 - QR INEXISTENTE
# ============================================================

def test_checkin_qr_inexistente(client):

    respuesta = validar(
        client,
        "SUBSONIC-INEXISTENTE"
    )

    assert respuesta.status_code == 404


# ============================================================
# TEST 4 - ENTRADA CANCELADA
# ============================================================

def test_checkin_entrada_cancelada(
    client,
    entrada_prueba
):

    with SessionLocal() as db:

        entrada = db.get(
            TicketDB,
            entrada_prueba["id"]
        )

        entrada.status = "cancelled"
        db.commit()

    respuesta = validar(
        client,
        entrada_prueba["qr_code"]
    )

    assert respuesta.status_code == 409

    assert consultar_estado(
        entrada_prueba["id"]
    ) == "cancelled"


# ============================================================
# TEST 5 - QR VACIO
# ============================================================

def test_checkin_qr_vacio(client):

    respuesta = validar(
        client,
        "  "
    )

    assert respuesta.status_code == 400


# ============================================================
# TEST 6 - SOLO ADMINISTRADORES
# ============================================================

def test_checkin_requiere_administrador(
    client,
    monkeypatch,
    entrada_prueba
):

    # Desactivar la autenticacion simulada de conftest
    # para comprobar los permisos reales.
    client.app.dependency_overrides.pop(
        get_token_BearerAuth,
        None
    )

    monkeypatch.setenv(
        "AUTH_SERVICE_URL",
        "http://auth-service-test"
    )

    class AuthSimulado:

        async def __aenter__(self):
            return self

        async def __aexit__(
            self,
            exc_type,
            exc,
            tb
        ):
            return False

        async def get(self, url, **kwargs):

            return httpx.Response(
                status_code=200,
                json={
                    "id": "usr_cliente",
                    "role": "client"
                }
            )

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: AuthSimulado()
    )

    respuesta = validar(
        client,
        entrada_prueba["qr_code"]
    )

    assert respuesta.status_code == 403

    # El intento no autorizado no debe
    # modificar la entrada.
    assert consultar_estado(
        entrada_prueba["id"]
    ) == "valid"
