
import pytest
from fastapi import HTTPException

from openapi_server.main import app
from openapi_server.database import SessionLocal
from openapi_server.db_models import (
    ProviderDB,
    SpaceDB,
    SpaceProposalDB
)
from openapi_server.security_api import obtener_usuario_actual

import openapi_server.apis.presupuestos_y_solicitudes_api as api


# ============================================================
# USUARIOS SIMULADOS
# ============================================================

PROVEEDOR = {
    "id": "usr_provider_001",
    "role": "provider",
    "is_active": True
}

OTRO_PROVEEDOR = {
    "id": "usr_provider_002",
    "role": "provider",
    "is_active": True
}

ADMINISTRADOR = {
    "id": "usr_admin_001",
    "role": "admin",
    "is_active": True
}

CLIENTE = {
    "id": "usr_client_001",
    "role": "client",
    "is_active": True
}

HEADERS = {
    "Authorization": "Bearer token_de_prueba"
}


# ============================================================
# DATOS AUXILIARES
# ============================================================

def datos_propuesta(
    provider_id="prov_001",
    space_id="spc_001",
    event_id="evt_001",
    presupuesto=1500.00
):
    return {
        "provider_id": provider_id,
        "space_id": space_id,
        "event_id": event_id,
        "budget_proposal": presupuesto,
        "setup_date": "2027-06-01"
    }


def crear_propuesta_en_bd(
    identificador="req_001",
    proveedor="prov_001",
    estado="pending"
):
    with SessionLocal() as db:
        db.add(
            SpaceProposalDB(
                id=identificador,
                provider_id=proveedor,
                space_id="spc_001",
                event_id="evt_001",
                budget_proposal=1500,
                setup_date=None,
                status=estado
            )
        )
        db.commit()


# ============================================================
# PREPARAR PROVEEDORES Y ESPACIOS
# ============================================================

@pytest.fixture
def datos_iniciales():

    with SessionLocal() as db:

        db.add_all([
            ProviderDB(
                id="prov_001",
                user_id=PROVEEDOR["id"],
                company_name="Empresa de Sonido",
                cif_nif="B12345678",
                service_category="Sonido",
                contact_email="sonido@ejemplo.com"
            ),
            ProviderDB(
                id="prov_002",
                user_id=OTRO_PROVEEDOR["id"],
                company_name="Empresa de Iluminacion",
                cif_nif="B87654321",
                service_category="Iluminacion",
                contact_email="luces@ejemplo.com"
            ),
            SpaceDB(
                id="spc_001",
                event_id="evt_001",
                name="Zona principal",
                dimensions="20x15 metros",
                base_price=1000,
                is_available=True
            )
        ])

        db.commit()


# ============================================================
# SIMULAR AUTENTICACION Y EVENTOS
# ============================================================

@pytest.fixture
def autenticar(monkeypatch):

    def configurar(usuario):

        async def usuario_actual():
            return usuario

        async def consultar_auth_simulado(ruta, token):

            if ruta == f"/users/{usuario['id']}":
                return usuario

            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado"
            )

        async def consultar_evento_simulado(event_id):

            if event_id == "evt_001":
                return {
                    "id": "evt_001",
                    "name": "Subsonic Festival"
                }

            raise HTTPException(
                status_code=404,
                detail="Evento no encontrado"
            )

        app.dependency_overrides[
            obtener_usuario_actual
        ] = usuario_actual

        monkeypatch.setattr(
            api,
            "consultar_auth",
            consultar_auth_simulado
        )

        monkeypatch.setattr(
            api,
            "consultar_evento",
            consultar_evento_simulado
        )

    yield configurar

    app.dependency_overrides.clear()


# ============================================================
# TEST 1 - CREAR PROPUESTA
# ============================================================

def test_crear_propuesta(
    client,
    datos_iniciales,
    autenticar
):

    autenticar(PROVEEDOR)

    respuesta = client.post(
        "/requests",
        json=datos_propuesta(),
        headers=HEADERS
    )

    assert respuesta.status_code == 201, respuesta.text

    propuesta = respuesta.json()

    assert propuesta["id"].startswith("req_")
    assert propuesta["provider_id"] == "prov_001"
    assert propuesta["space_id"] == "spc_001"
    assert propuesta["status"] == "pending"


# ============================================================
# TEST 2 - IMPEDIR PROPUESTA DUPLICADA
# ============================================================

def test_no_duplicar_propuesta_pendiente(
    client,
    datos_iniciales,
    autenticar
):

    autenticar(PROVEEDOR)

    primera = client.post(
        "/requests",
        json=datos_propuesta(),
        headers=HEADERS
    )

    segunda = client.post(
        "/requests",
        json=datos_propuesta(),
        headers=HEADERS
    )

    assert primera.status_code == 201, primera.text
    assert segunda.status_code == 409, segunda.text


# ============================================================
# TEST 3 - PRESUPUESTO INVALIDO
# ============================================================

def test_presupuesto_negativo(
    client,
    datos_iniciales,
    autenticar
):

    autenticar(PROVEEDOR)

    respuesta = client.post(
        "/requests",
        json=datos_propuesta(presupuesto=-100),
        headers=HEADERS
    )

    assert respuesta.status_code in (400, 422)


# ============================================================
# TEST 4 - IMPEDIR PROPUESTAS AJENAS
# ============================================================

def test_no_enviar_propuesta_de_otro_proveedor(
    client,
    datos_iniciales,
    autenticar
):

    autenticar(PROVEEDOR)

    respuesta = client.post(
        "/requests",
        json=datos_propuesta(provider_id="prov_002"),
        headers=HEADERS
    )

    assert respuesta.status_code == 403


# ============================================================
# TEST 5 - CLIENTE NO PUEDE ENVIAR PROPUESTAS
# ============================================================

def test_cliente_no_puede_enviar_propuesta(
    client,
    datos_iniciales,
    autenticar
):

    autenticar(CLIENTE)

    respuesta = client.post(
        "/requests",
        json=datos_propuesta(),
        headers=HEADERS
    )

    assert respuesta.status_code == 403


# ============================================================
# TEST 6 - CONSULTAR PROPUESTAS PROPIAS
# ============================================================

def test_consultar_propuestas_propias(
    client,
    datos_iniciales,
    autenticar
):

    crear_propuesta_en_bd()
    autenticar(PROVEEDOR)

    respuesta = client.get(
        "/requests/provider/prov_001"
    )

    assert respuesta.status_code == 200, respuesta.text
    assert len(respuesta.json()) == 1
    assert respuesta.json()[0]["id"] == "req_001"


# ============================================================
# TEST 7 - IMPEDIR CONSULTA AJENA
# ============================================================

def test_no_consultar_propuestas_ajenas(
    client,
    datos_iniciales,
    autenticar
):

    crear_propuesta_en_bd()
    autenticar(OTRO_PROVEEDOR)

    respuesta = client.get(
        "/requests/provider/prov_001"
    )

    assert respuesta.status_code == 403


# ============================================================
# TEST 8 - ADMINISTRADOR CONSULTA PROPUESTAS
# ============================================================

def test_admin_consulta_propuestas_evento(
    client,
    datos_iniciales,
    autenticar
):

    crear_propuesta_en_bd()
    autenticar(ADMINISTRADOR)

    respuesta = client.get(
        "/requests/event/evt_001"
    )

    assert respuesta.status_code == 200, respuesta.text
    assert len(respuesta.json()) == 1


# ============================================================
# TEST 9 - PROVEEDOR NO CONSULTA TODO EL EVENTO
# ============================================================

def test_proveedor_no_consulta_todo_el_evento(
    client,
    datos_iniciales,
    autenticar
):

    autenticar(PROVEEDOR)

    respuesta = client.get(
        "/requests/event/evt_001"
    )

    assert respuesta.status_code == 403


# ============================================================
# TEST 10 - APROBAR PROPUESTA
# ============================================================

def test_aprobar_propuesta(
    client,
    datos_iniciales,
    autenticar
):

    crear_propuesta_en_bd()
    autenticar(ADMINISTRADOR)

    respuesta = client.put(
        "/requests/req_001/status",
        json={"status": "approved"}
    )

    assert respuesta.status_code == 200, respuesta.text

    with SessionLocal() as db:
        propuesta = db.get(SpaceProposalDB, "req_001")
        espacio = db.get(SpaceDB, "spc_001")

        assert propuesta.status == "approved"
        assert espacio.is_available is False


# ============================================================
# TEST 11 - RECHAZAR PROPUESTA
# ============================================================

def test_rechazar_propuesta(
    client,
    datos_iniciales,
    autenticar
):

    crear_propuesta_en_bd()
    autenticar(ADMINISTRADOR)

    respuesta = client.put(
        "/requests/req_001/status",
        json={"status": "rejected"}
    )

    assert respuesta.status_code == 200, respuesta.text

    with SessionLocal() as db:
        propuesta = db.get(SpaceProposalDB, "req_001")
        espacio = db.get(SpaceDB, "spc_001")

        assert propuesta.status == "rejected"
        assert espacio.is_available is True


# ============================================================
# TEST 12 - IMPEDIR SEGUNDA ADJUDICACION
# ============================================================

def test_no_aprobar_dos_propuestas_mismo_espacio(
    client,
    datos_iniciales,
    autenticar
):

    crear_propuesta_en_bd(
        identificador="req_001",
        proveedor="prov_001"
    )

    crear_propuesta_en_bd(
        identificador="req_002",
        proveedor="prov_002"
    )

    autenticar(ADMINISTRADOR)

    primera = client.put(
        "/requests/req_001/status",
        json={"status": "approved"}
    )

    segunda = client.put(
        "/requests/req_002/status",
        json={"status": "approved"}
    )

    assert primera.status_code == 200, primera.text
    assert segunda.status_code == 409, segunda.text


# ============================================================
# TEST 13 - IMPEDIR CAMBIAR PROPUESTA RESUELTA
# ============================================================

def test_no_modificar_propuesta_resuelta(
    client,
    datos_iniciales,
    autenticar
):

    crear_propuesta_en_bd(
        estado="rejected"
    )

    autenticar(ADMINISTRADOR)

    respuesta = client.put(
        "/requests/req_001/status",
        json={"status": "approved"}
    )

    assert respuesta.status_code == 409


# ============================================================
# TEST 14 - SOLO ADMINISTRADORES RESUELVEN
# ============================================================

def test_proveedor_no_aprueba_propuesta(
    client,
    datos_iniciales,
    autenticar
):

    crear_propuesta_en_bd()
    autenticar(PROVEEDOR)

    respuesta = client.put(
        "/requests/req_001/status",
        json={"status": "approved"}
    )

    assert respuesta.status_code == 403


# ============================================================
# TEST 15 - DOS ADJUDICACIONES SIMULTANEAS
# ============================================================

def test_adjudicaciones_concurrentes(
    client,
    datos_iniciales,
    autenticar
):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    crear_propuesta_en_bd(
        identificador="req_001",
        proveedor="prov_001"
    )

    crear_propuesta_en_bd(
        identificador="req_002",
        proveedor="prov_002"
    )

    autenticar(ADMINISTRADOR)

    barrera = Barrier(2)

    def aprobar(propuesta_id):
        from fastapi.testclient import TestClient

        # Cada hilo utiliza su propio cliente HTTP.
        with TestClient(app) as cliente:
            barrera.wait(timeout=10)

            respuesta = cliente.put(
                f"/requests/{propuesta_id}/status",
                json={"status": "approved"}
            )

            return respuesta.status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        futuro_1 = executor.submit(aprobar, "req_001")
        futuro_2 = executor.submit(aprobar, "req_002")

        resultados = [
            futuro_1.result(timeout=20),
            futuro_2.result(timeout=20)
        ]

    # Una adjudicacion debe ganar y la otra rechazarse.
    assert sorted(resultados) == [200, 409], resultados

    with SessionLocal() as db:
        propuestas = db.query(SpaceProposalDB).filter(
            SpaceProposalDB.space_id == "spc_001"
        ).all()

        aprobadas = [
            propuesta
            for propuesta in propuestas
            if propuesta.status == "approved"
        ]

        espacio = db.get(SpaceDB, "spc_001")

        assert len(aprobadas) == 1
        assert espacio.is_available is False


# ============================================================
# TEST 16 - AUTENTICACION NO DISPONIBLE
# ============================================================

def test_propuesta_auth_no_disponible(
    client,
    datos_iniciales,
    autenticar,
    monkeypatch
):

    autenticar(PROVEEDOR)

    async def auth_no_disponible(ruta, token):
        raise HTTPException(
            status_code=503,
            detail="Autenticacion no disponible"
        )

    monkeypatch.setattr(
        api,
        "consultar_auth",
        auth_no_disponible
    )

    respuesta = client.post(
        "/requests",
        json=datos_propuesta(),
        headers=HEADERS
    )

    assert respuesta.status_code == 503

    with SessionLocal() as db:
        assert db.query(SpaceProposalDB).count() == 0


# ============================================================
# TEST 17 - EVENTOS NO DISPONIBLE
# ============================================================

def test_propuesta_eventos_no_disponible(
    client,
    datos_iniciales,
    autenticar,
    monkeypatch
):

    autenticar(PROVEEDOR)

    async def eventos_no_disponible(event_id):
        raise HTTPException(
            status_code=503,
            detail="Eventos no disponible"
        )

    monkeypatch.setattr(
        api,
        "consultar_evento",
        eventos_no_disponible
    )

    respuesta = client.post(
        "/requests",
        json=datos_propuesta(),
        headers=HEADERS
    )

    assert respuesta.status_code == 503

    with SessionLocal() as db:
        assert db.query(SpaceProposalDB).count() == 0
