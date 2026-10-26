
import pytest
from fastapi import HTTPException

from openapi_server.main import app
from openapi_server.security_api import obtener_usuario_actual
import openapi_server.apis.servicios_y_espacios_api as espacios_api


# ============================================================
# USUARIOS SIMULADOS
# ============================================================

ADMINISTRADOR = {
    "id": "usr_admin_001",
    "role": "admin",
    "is_active": True
}

PROVEEDOR = {
    "id": "usr_provider_001",
    "role": "provider",
    "is_active": True
}

CLIENTE = {
    "id": "usr_client_001",
    "role": "client",
    "is_active": True
}


# ============================================================
# DATOS DE PRUEBA
# ============================================================

def datos_servicio():
    return {
        "name": "Sonido",
        "description": "Equipamiento de sonido profesional"
    }


def datos_espacio():
    return {
        "event_id": "evt_001",
        "name": "Zona principal",
        "dimensions": "20x15 metros",
        "base_price": 1200.50,
        "is_available": True
    }


# ============================================================
# AUTENTICACION SIMULADA
# ============================================================

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


# ============================================================
# MICROSERVICIO DE EVENTOS SIMULADO
# ============================================================

@pytest.fixture
def simular_eventos(monkeypatch):

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

    monkeypatch.setattr(
        espacios_api,
        "consultar_evento",
        consultar_evento_simulado
    )


# ============================================================
# TEST 1 - ADMINISTRADOR CREA SERVICIO
# ============================================================

def test_administrador_crea_servicio(
    client,
    autenticar
):

    autenticar(ADMINISTRADOR)

    respuesta = client.post(
        "/external-services",
        json=datos_servicio()
    )

    assert respuesta.status_code == 201, respuesta.text

    servicio = respuesta.json()

    assert servicio["name"] == "Sonido"
    assert servicio["id"].startswith("srv_")


# ============================================================
# TEST 2 - LOS SERVICIOS SON PUBLICOS
# ============================================================

def test_consultar_servicios_publicamente(
    client,
    autenticar
):

    autenticar(ADMINISTRADOR)

    registro = client.post(
        "/external-services",
        json=datos_servicio()
    )

    assert registro.status_code == 201, registro.text

    app.dependency_overrides.clear()

    respuesta = client.get("/external-services")

    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 1
    assert respuesta.json()[0]["name"] == "Sonido"


# ============================================================
# TEST 3 - PROVEEDOR NO PUEDE CREAR SERVICIOS
# ============================================================

def test_proveedor_no_puede_crear_servicio(
    client,
    autenticar
):

    autenticar(PROVEEDOR)

    respuesta = client.post(
        "/external-services",
        json=datos_servicio()
    )

    assert respuesta.status_code == 403


# ============================================================
# TEST 4 - CLIENTE NO PUEDE CREAR SERVICIOS
# ============================================================

def test_cliente_no_puede_crear_servicio(
    client,
    autenticar
):

    autenticar(CLIENTE)

    respuesta = client.post(
        "/external-services",
        json=datos_servicio()
    )

    assert respuesta.status_code == 403


# ============================================================
# TEST 5 - ADMINISTRADOR CREA ESPACIO
# ============================================================

def test_administrador_crea_espacio(
    client,
    autenticar,
    simular_eventos
):

    autenticar(ADMINISTRADOR)

    respuesta = client.post(
        "/spaces",
        json=datos_espacio()
    )

    assert respuesta.status_code == 201, respuesta.text

    espacio = respuesta.json()

    assert espacio["id"].startswith("spc_")
    assert espacio["event_id"] == "evt_001"
    assert espacio["name"] == "Zona principal"
    assert espacio["base_price"] == 1200.50
    assert espacio["is_available"] is True


# ============================================================
# TEST 6 - CONSULTAR ESPACIOS DE UN EVENTO
# ============================================================

def test_consultar_espacios_evento(
    client,
    autenticar,
    simular_eventos
):

    autenticar(ADMINISTRADOR)

    registro = client.post(
        "/spaces",
        json=datos_espacio()
    )

    assert registro.status_code == 201, registro.text

    app.dependency_overrides.clear()

    respuesta = client.get(
        "/spaces",
        params={"event_id": "evt_001"}
    )

    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 1
    assert respuesta.json()[0]["name"] == "Zona principal"


# ============================================================
# TEST 7 - EVITAR ESPACIOS DUPLICADOS
# ============================================================

def test_no_duplicar_espacio(
    client,
    autenticar,
    simular_eventos
):

    autenticar(ADMINISTRADOR)

    primera = client.post(
        "/spaces",
        json=datos_espacio()
    )

    segunda = client.post(
        "/spaces",
        json=datos_espacio()
    )

    assert primera.status_code == 201, primera.text
    assert segunda.status_code == 409, segunda.text


# ============================================================
# TEST 8 - EVENTO INEXISTENTE
# ============================================================

def test_no_crear_espacio_evento_inexistente(
    client,
    autenticar,
    simular_eventos
):

    autenticar(ADMINISTRADOR)

    datos = datos_espacio()
    datos["event_id"] = "evt_inexistente"

    respuesta = client.post(
        "/spaces",
        json=datos
    )

    assert respuesta.status_code == 404


# ============================================================
# TEST 9 - PROVEEDOR NO PUEDE CREAR ESPACIOS
# ============================================================

def test_proveedor_no_puede_crear_espacio(
    client,
    autenticar,
    simular_eventos
):

    autenticar(PROVEEDOR)

    respuesta = client.post(
        "/spaces",
        json=datos_espacio()
    )

    assert respuesta.status_code == 403


# ============================================================
# TEST 10 - PRECIO NEGATIVO
# ============================================================

def test_no_crear_espacio_precio_negativo(
    client,
    autenticar,
    simular_eventos
):

    autenticar(ADMINISTRADOR)

    datos = datos_espacio()
    datos["base_price"] = -100

    respuesta = client.post(
        "/spaces",
        json=datos
    )

    assert respuesta.status_code in (400, 422)


# ============================================================
# TEST 11 - EVENTOS NO DISPONIBLE
# ============================================================

def test_eventos_no_disponible(
    client,
    autenticar,
    monkeypatch
):

    autenticar(ADMINISTRADOR)

    async def evento_no_disponible(event_id):
        raise HTTPException(
            status_code=503,
            detail="Eventos no disponible"
        )

    monkeypatch.setattr(
        espacios_api,
        "consultar_evento",
        evento_no_disponible
    )

    respuesta = client.post(
        "/spaces",
        json=datos_espacio()
    )

    assert respuesta.status_code == 503
