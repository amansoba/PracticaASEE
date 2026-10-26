
import httpx
import pytest

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from openapi_server.security_api import (
    consultar_usuario_autenticado,
    get_admin_BearerAuth
)


# ============================================================
# TEST 1: UN CLIENTE NO PUEDE ACTUAR COMO ADMINISTRADOR
# ============================================================

@pytest.mark.asyncio
async def test_cliente_no_es_administrador(monkeypatch):

    async def simular_consulta(credentials):
        return {
            "id": "usr_cliente",
            "role": "client"
        }

    monkeypatch.setattr(
        "openapi_server.security_api.consultar_usuario_autenticado",
        simular_consulta
    )

    credenciales = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="token_cliente"
    )

    with pytest.raises(HTTPException) as error:
        await get_admin_BearerAuth(credenciales)

    assert error.value.status_code == 403


# ============================================================
# TEST 2: UN ADMINISTRADOR TIENE ACCESO
# ============================================================

@pytest.mark.asyncio
async def test_administrador_autorizado(monkeypatch):

    async def simular_consulta(credentials):
        return {
            "id": "usr_admin",
            "role": "admin"
        }

    monkeypatch.setattr(
        "openapi_server.security_api.consultar_usuario_autenticado",
        simular_consulta
    )

    credenciales = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="token_admin"
    )

    token = await get_admin_BearerAuth(credenciales)

    assert token.sub == "usr_admin"


# ============================================================
# TEST 3: AUTENTICACION RECHAZA UN JWT INVALIDO
# ============================================================

@pytest.mark.asyncio
async def test_token_rechazado_por_autenticacion(monkeypatch):

    def responder(request):
        return httpx.Response(
            status_code=401,
            json={"detail": "Token invalido"}
        )

    transporte = httpx.MockTransport(responder)

    cliente_original = httpx.AsyncClient

    def cliente_simulado(*args, **kwargs):
        kwargs["transport"] = transporte
        return cliente_original(*args, **kwargs)

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        cliente_simulado
    )

    credenciales = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="token_invalido"
    )

    with pytest.raises(HTTPException) as error:
        await consultar_usuario_autenticado(
            credenciales
        )

    assert error.value.status_code == 401


# ============================================================
# TEST 4: AUTENTICACION NO ESTA DISPONIBLE
# ============================================================

@pytest.mark.asyncio
async def test_autenticacion_no_disponible(monkeypatch):

    def responder(request):
        raise httpx.ConnectError(
            "Conexion rechazada",
            request=request
        )

    transporte = httpx.MockTransport(responder)

    cliente_original = httpx.AsyncClient

    def cliente_simulado(*args, **kwargs):
        kwargs["transport"] = transporte
        return cliente_original(*args, **kwargs)

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        cliente_simulado
    )

    credenciales = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="token_valido"
    )

    with pytest.raises(HTTPException) as error:
        await consultar_usuario_autenticado(
            credenciales
        )

    assert error.value.status_code == 503
