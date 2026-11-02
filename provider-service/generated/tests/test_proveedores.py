
import pytest
from fastapi import HTTPException

from openapi_server.main import app
from openapi_server.security_api import obtener_usuario_actual
import openapi_server.security_api as security_api


# ============================================================
# USUARIOS SIMULADOS
# ============================================================

PROVEEDOR = {
    "id": "usr_proveedor_001",
    "role": "provider",
    "is_active": True
}

OTRO_PROVEEDOR = {
    "id": "usr_proveedor_002",
    "role": "provider",
    "is_active": True
}

ADMINISTRADOR = {
    "id": "usr_admin_001",
    "role": "admin",
    "is_active": True
}

CLIENTE = {
    "id": "usr_cliente_001",
    "role": "client",
    "is_active": True
}


# ============================================================
# DATOS DE REGISTRO
# ============================================================

def datos_empresa(
    user_id="usr_proveedor_001",
    cif_nif="B12345678"
):
    return {
        "user_id": user_id,
        "company_name": "Sonido Extremadura",
        "cif_nif": cif_nif,
        "service_category": "Sonido",
        "contact_email": "contacto@sonidoejemplo.com"
    }


# ============================================================
# CONFIGURACION DE AUTENTICACION SIMULADA
# ============================================================

@pytest.fixture
def autenticar(monkeypatch):

    def configurar(usuario):

        async def usuario_actual():
            return usuario

        async def consultar_auth_simulado(ruta, token):

            if ruta == "/users/me":
                return usuario

            if ruta.startswith("/users/"):
                identificador = ruta.removeprefix("/users/")

                if identificador == usuario["id"]:
                    return usuario

                raise HTTPException(
                    status_code=404,
                    detail="Usuario no encontrado"
                )

            raise AssertionError(
                f"Consulta inesperada a Autenticacion: {ruta}"
            )

        app.dependency_overrides[
            obtener_usuario_actual
        ] = usuario_actual

        monkeypatch.setattr(
            security_api,
            "consultar_auth",
            consultar_auth_simulado
        )

    yield configurar

    app.dependency_overrides.clear()


# ============================================================
# TEST 1 - REGISTRAR PROVEEDOR
# ============================================================

def test_registrar_proveedor(
    client,
    autenticar
):

    autenticar(PROVEEDOR)

    respuesta = client.post(
        "/providers",
        json=datos_empresa(),
        headers={
            "Authorization": "Bearer token_de_prueba"
        }
    )

    assert respuesta.status_code == 201, respuesta.text

    proveedor = respuesta.json()

    assert proveedor["user_id"] == PROVEEDOR["id"]
    assert proveedor["company_name"] == "Sonido Extremadura"
    assert proveedor["cif_nif"] == "B12345678"
    assert proveedor["id"].startswith("prov_")


# ============================================================
# TEST 2 - CONSULTAR PROVEEDOR EXISTENTE
# ============================================================

def test_consultar_proveedor(
    client,
    autenticar
):

    autenticar(PROVEEDOR)

    registro = client.post(
        "/providers",
        json=datos_empresa(),
        headers={
            "Authorization": "Bearer token_de_prueba"
        }
    )

    assert registro.status_code == 201, registro.text

    proveedor_id = registro.json()["id"]

    respuesta = client.get(
        f"/providers/{proveedor_id}"
    )

    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["id"] == proveedor_id


# ============================================================
# TEST 3 - PROVEEDOR INEXISTENTE
# ============================================================

def test_proveedor_inexistente(
    client,
    autenticar
):

    autenticar(PROVEEDOR)

    respuesta = client.get(
        "/providers/prov_inexistente"
    )

    assert respuesta.status_code == 404


# ============================================================
# TEST 4 - REGISTRO DUPLICADO
# ============================================================

def test_no_registrar_dos_empresas_mismo_usuario(
    client,
    autenticar
):

    autenticar(PROVEEDOR)

    headers = {
        "Authorization": "Bearer token_de_prueba"
    }

    primera = client.post(
        "/providers",
        json=datos_empresa(),
        headers=headers
    )

    segunda = client.post(
        "/providers",
        json=datos_empresa(cif_nif="B87654321"),
        headers=headers
    )

    assert primera.status_code == 201, primera.text
    assert segunda.status_code == 409, segunda.text


# ============================================================
# TEST 5 - UN CLIENTE NO PUEDE REGISTRAR EMPRESAS
# ============================================================

def test_cliente_no_puede_registrar_empresa(
    client,
    autenticar
):

    autenticar(CLIENTE)

    respuesta = client.post(
        "/providers",
        json=datos_empresa(
            user_id=CLIENTE["id"]
        ),
        headers={
            "Authorization": "Bearer token_de_prueba"
        }
    )

    assert respuesta.status_code == 403


# ============================================================
# TEST 6 - IMPEDIR SUPLANTACION DE PROVEEDOR
# ============================================================

def test_no_registrar_empresa_de_otro_usuario(
    client,
    autenticar
):

    autenticar(PROVEEDOR)

    respuesta = client.post(
        "/providers",
        json=datos_empresa(
            user_id=OTRO_PROVEEDOR["id"]
        ),
        headers={
            "Authorization": "Bearer token_de_prueba"
        }
    )

    assert respuesta.status_code == 403


# ============================================================
# TEST 7 - SOLO ADMINISTRADORES PUEDEN LISTAR
# ============================================================

def test_proveedor_no_puede_listar_empresas(
    client,
    autenticar
):

    autenticar(PROVEEDOR)

    respuesta = client.get(
        "/providers"
    )

    assert respuesta.status_code == 403


# ============================================================
# TEST 8 - ADMINISTRADOR PUEDE LISTAR
# ============================================================

def test_administrador_puede_listar_empresas(
    client,
    autenticar
):

    autenticar(ADMINISTRADOR)

    respuesta = client.get(
        "/providers"
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == []


# ============================================================
# TEST 9 - AUTENTICACION NO DISPONIBLE
# ============================================================

def test_error_al_consultar_autenticacion(
    client,
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
        security_api,
        "consultar_auth",
        auth_no_disponible
    )

    respuesta = client.post(
        "/providers",
        json=datos_empresa(),
        headers={
            "Authorization": "Bearer token_de_prueba"
        }
    )

    assert respuesta.status_code == 503


# ============================================================
# TEST 10 - CONSULTAR MI EMPRESA
# ============================================================

def test_consultar_mi_empresa(client, autenticar):

    autenticar(PROVEEDOR)

    headers = {
        "Authorization": "Bearer token_de_prueba"
    }

    registro = client.post(
        "/providers",
        json=datos_empresa(),
        headers=headers
    )

    assert registro.status_code == 201, registro.text

    proveedor_id = registro.json()["id"]

    respuesta = client.get(
        "/providers/me",
        headers=headers
    )

    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["id"] == proveedor_id
    assert respuesta.json()["user_id"] == PROVEEDOR["id"]


# ============================================================
# TEST 11 - CLIENTE NO PUEDE CONSULTAR MI EMPRESA
# ============================================================

def test_cliente_no_puede_consultar_mi_empresa(
    client,
    autenticar
):

    autenticar(CLIENTE)

    respuesta = client.get(
        "/providers/me",
        headers={
            "Authorization": "Bearer token_de_prueba"
        }
    )

    assert respuesta.status_code == 403


# ============================================================
# TEST 12 - PROVEEDOR SIN EMPRESA REGISTRADA
# ============================================================

def test_consultar_mi_empresa_inexistente(
    client,
    autenticar
):

    autenticar(PROVEEDOR)

    respuesta = client.get(
        "/providers/me",
        headers={
            "Authorization": "Bearer token_de_prueba"
        }
    )

    assert respuesta.status_code == 404
