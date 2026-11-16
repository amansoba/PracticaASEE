
import pytest

from fastapi import HTTPException
from sqlalchemy import select

from openapi_server.main import app
from openapi_server.database import SessionLocal
from openapi_server.db_models import (
    ProviderDB,
    SpaceDB,
    SpaceProposalDB
)
from openapi_server.security_api import obtener_usuario_actual

import openapi_server.apis.servicios_y_espacios_api as api_original
import openapi_server.apis.administracion_servicios_espacios_api as api_admin


ADMIN = {"id": "usr_admin_test", "role": "admin"}
CLIENTE = {"id": "usr_cliente_test", "role": "client"}


@pytest.fixture
def autenticar():

    def configurar(usuario):
        async def usuario_actual():
            return usuario

        app.dependency_overrides[
            obtener_usuario_actual
        ] = usuario_actual

    yield configurar

    app.dependency_overrides.clear()


@pytest.fixture
def simular_eventos(monkeypatch):

    async def consultar_evento_simulado(event_id):
        if event_id in ("evt_001", "evt_002"):
            return {
                "id": event_id,
                "name": "Festival de prueba"
            }

        raise HTTPException(
            status_code=404,
            detail="Evento no encontrado"
        )

    monkeypatch.setattr(
        api_original,
        "consultar_evento",
        consultar_evento_simulado
    )

    monkeypatch.setattr(
        api_admin,
        "consultar_evento",
        consultar_evento_simulado
    )


def crear_servicio(client, nombre="Sonido"):

    respuesta = client.post(
        "/external-services",
        json={
            "name": nombre,
            "description": "Servicio de prueba"
        }
    )

    assert respuesta.status_code == 201, respuesta.text

    return respuesta.json()


def datos_espacio(
    nombre="Zona principal",
    evento="evt_001"
):
    return {
        "event_id": evento,
        "name": nombre,
        "dimensions": "20x15 metros",
        "base_price": 1200.50,
        "is_available": True
    }


def crear_espacio(client, nombre="Zona principal"):

    respuesta = client.post(
        "/spaces",
        json=datos_espacio(nombre)
    )

    assert respuesta.status_code == 201, respuesta.text

    return respuesta.json()


# ============================================================
# TEST 1 - EDITAR SERVICIO EXTERNO
# ============================================================

def test_actualizar_servicio(client, autenticar):

    autenticar(ADMIN)
    servicio = crear_servicio(client)

    respuesta = client.put(
        f"/external-services/{servicio['id']}",
        json={
            "name": "Sonido profesional",
            "description": "Equipamiento avanzado"
        }
    )

    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["id"] == servicio["id"]
    assert respuesta.json()["name"] == "Sonido profesional"

    listado = client.get("/external-services")

    assert listado.status_code == 200
    assert listado.json()[0]["name"] == "Sonido profesional"


# ============================================================
# TEST 2 - ELIMINAR SERVICIO EXTERNO
# ============================================================

def test_eliminar_servicio(client, autenticar):

    autenticar(ADMIN)
    servicio = crear_servicio(client)

    respuesta = client.delete(
        f"/external-services/{servicio['id']}"
    )

    assert respuesta.status_code == 204

    listado = client.get("/external-services")

    assert listado.status_code == 200
    assert listado.json() == []


# ============================================================
# TEST 3 - SERVICIO INEXISTENTE
# ============================================================

def test_servicio_inexistente(client, autenticar):

    autenticar(ADMIN)

    respuesta = client.put(
        "/external-services/srv_inexistente",
        json={
            "name": "Otro servicio"
        }
    )

    assert respuesta.status_code == 404


# ============================================================
# TEST 4 - DATOS INVALIDOS
# ============================================================

def test_servicio_nombre_vacio(client, autenticar):

    autenticar(ADMIN)
    servicio = crear_servicio(client)

    respuesta = client.put(
        f"/external-services/{servicio['id']}",
        json={"name": "   "}
    )

    assert respuesta.status_code == 400


# ============================================================
# TEST 5 - SOLO ADMINISTRADORES
# ============================================================

def test_cliente_no_edita_servicio(client, autenticar):

    autenticar(ADMIN)
    servicio = crear_servicio(client)

    autenticar(CLIENTE)

    respuesta = client.delete(
        f"/external-services/{servicio['id']}"
    )

    assert respuesta.status_code == 403


# ============================================================
# TEST 6 - EDITAR ESPACIO
# ============================================================

def test_actualizar_espacio(
    client,
    autenticar,
    simular_eventos
):

    autenticar(ADMIN)
    espacio = crear_espacio(client)

    nuevos_datos = datos_espacio(
        nombre="Zona VIP"
    )
    nuevos_datos["base_price"] = 1500.75

    respuesta = client.put(
        f"/spaces/{espacio['id']}",
        json=nuevos_datos
    )

    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["id"] == espacio["id"]
    assert respuesta.json()["name"] == "Zona VIP"
    assert respuesta.json()["base_price"] == 1500.75

    listado = client.get(
        "/spaces",
        params={"event_id": "evt_001"}
    )

    assert listado.status_code == 200
    assert listado.json()[0]["name"] == "Zona VIP"


# ============================================================
# TEST 7 - ELIMINAR ESPACIO
# ============================================================

def test_eliminar_espacio(
    client,
    autenticar,
    simular_eventos
):

    autenticar(ADMIN)
    espacio = crear_espacio(client)

    respuesta = client.delete(
        f"/spaces/{espacio['id']}"
    )

    assert respuesta.status_code == 204

    listado = client.get(
        "/spaces",
        params={"event_id": "evt_001"}
    )

    assert listado.status_code == 200
    assert listado.json() == []


# ============================================================
# TEST 8 - ESPACIO INEXISTENTE
# ============================================================

def test_espacio_inexistente(
    client,
    autenticar,
    simular_eventos
):

    autenticar(ADMIN)

    respuesta = client.delete(
        "/spaces/spc_inexistente"
    )

    assert respuesta.status_code == 404


# ============================================================
# TEST 9 - NO DUPLICAR NOMBRE DE ESPACIO
# ============================================================

def test_no_duplicar_nombre_espacio(
    client,
    autenticar,
    simular_eventos
):

    autenticar(ADMIN)

    primero = crear_espacio(
        client,
        "Zona principal"
    )
    segundo = crear_espacio(
        client,
        "Zona secundaria"
    )

    respuesta = client.put(
        f"/spaces/{segundo['id']}",
        json=datos_espacio("Zona principal")
    )

    assert respuesta.status_code == 409

    with SessionLocal() as db:
        original = db.get(SpaceDB, segundo["id"])
        assert original.name == "Zona secundaria"


# ============================================================
# TEST 10 - NO ELIMINAR ESPACIO CON PROPUESTAS
# ============================================================

def test_no_eliminar_espacio_con_propuestas(
    client,
    autenticar,
    simular_eventos
):

    autenticar(ADMIN)
    espacio = crear_espacio(client)

    with SessionLocal() as db:

        db.add(
            ProviderDB(
                id="prov_prueba",
                user_id="usr_proveedor_prueba",
                company_name="Empresa de prueba",
                cif_nif="B12345678",
                service_category="Sonido",
                contact_email="test@ejemplo.com"
            )
        )

        db.flush()

        db.add(
            SpaceProposalDB(
                id="req_prueba",
                space_id=espacio["id"],
                provider_id="prov_prueba",
                event_id="evt_001",
                budget_proposal=1000,
                setup_date=None,
                status="pending"
            )
        )

        db.commit()

    respuesta = client.delete(
        f"/spaces/{espacio['id']}"
    )

    assert respuesta.status_code == 409

    with SessionLocal() as db:
        assert db.get(SpaceDB, espacio["id"]) is not None


# ============================================================
# TEST 11 - NO TRASLADAR PROPUESTAS ENTRE EVENTOS
# ============================================================

def test_no_cambiar_evento_con_propuestas(
    client,
    autenticar,
    simular_eventos
):

    autenticar(ADMIN)
    espacio = crear_espacio(client)

    with SessionLocal() as db:
        db.add(
            ProviderDB(
                id="prov_prueba",
                user_id="usr_proveedor_prueba",
                company_name="Empresa de prueba",
                cif_nif="B12345678",
                service_category="Sonido",
                contact_email="test@ejemplo.com"
            )
        )

        db.flush()

        db.add(
            SpaceProposalDB(
                id="req_prueba",
                space_id=espacio["id"],
                provider_id="prov_prueba",
                event_id="evt_001",
                budget_proposal=1000,
                setup_date=None,
                status="pending"
            )
        )

        db.commit()

    respuesta = client.put(
        f"/spaces/{espacio['id']}",
        json=datos_espacio(
            "Zona principal",
            "evt_002"
        )
    )

    assert respuesta.status_code == 409

    with SessionLocal() as db:
        original = db.get(SpaceDB, espacio["id"])
        assert original.event_id == "evt_001"


# ============================================================
# TEST 12 - CLIENTE NO PUEDE EDITAR ESPACIOS
# ============================================================

def test_cliente_no_edita_espacio(
    client,
    autenticar,
    simular_eventos
):

    autenticar(ADMIN)
    espacio = crear_espacio(client)

    autenticar(CLIENTE)

    respuesta = client.put(
        f"/spaces/{espacio['id']}",
        json=datos_espacio("Zona cambiada")
    )

    assert respuesta.status_code == 403
