
import pytest

from fastapi import HTTPException
from sqlalchemy import select

from openapi_server.database import SessionLocal
from openapi_server.db_models import UserDB
from openapi_server.auth_security import verificar_password
from openapi_server.auth_flows import (
    PasswordResetDB,
    hash_token
)


USUARIO = {
    "name": "Usuario Prueba",
    "email": "prueba@subsonic.com",
    "password": "PruebaSegura123!",
    "phone": "600123456"
}


def registrar_usuario(client, datos=None):
    return client.post(
        "/auth/register",
        json=datos or USUARIO
    )


def iniciar_sesion(client, email=None, password=None):
    return client.post(
        "/auth/login",
        json={
            "email": email or USUARIO["email"],
            "password": password or USUARIO["password"]
        }
    )


def obtener_token(client):
    respuesta = iniciar_sesion(client)
    assert respuesta.status_code == 200
    return respuesta.json()["access_token"]


def cabecera_token(token):
    return {
        "Authorization": f"Bearer {token}"
    }


def test_registro_correcto(client):
    respuesta = registrar_usuario(client)

    assert respuesta.status_code == 201

    datos = respuesta.json()

    assert datos["name"] == USUARIO["name"]
    assert datos["email"] == USUARIO["email"]
    assert datos["role"] == "client"
    assert datos["id"].startswith("usr_")
    assert "password" not in datos
    assert "password_hash" not in datos


def test_registro_guarda_password_cifrada(client):
    registrar_usuario(client)

    with SessionLocal() as db:
        usuario = db.scalar(
            select(UserDB).where(
                UserDB.email == USUARIO["email"]
            )
        )

        assert usuario is not None
        assert usuario.password_hash != USUARIO["password"]
        assert usuario.password_hash.startswith("$argon2")
        assert verificar_password(
            USUARIO["password"],
            usuario.password_hash
        )


def test_registro_correo_duplicado(client):
    primera = registrar_usuario(client)
    segunda = registrar_usuario(client)

    assert primera.status_code == 201
    assert segunda.status_code == 400


def test_registro_password_corta(client):
    datos = USUARIO.copy()
    datos["password"] = "123"

    respuesta = registrar_usuario(client, datos)

    assert respuesta.status_code in (400, 422)


def test_login_correcto(client):
    registrar_usuario(client)

    respuesta = iniciar_sesion(client)

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert datos["access_token"]
    assert datos["token_type"] == "Bearer"
    assert datos["expires_in"] == 3600
    assert datos["user"]["role"] == "client"


def test_login_password_incorrecta(client):
    registrar_usuario(client)

    respuesta = iniciar_sesion(
        client,
        password="ContrasenaIncorrecta123"
    )

    assert respuesta.status_code == 401


def test_login_usuario_inexistente(client):
    respuesta = iniciar_sesion(
        client,
        email="inexistente@subsonic.com"
    )

    assert respuesta.status_code == 401


def test_logout_correcto(client):
    registrar_usuario(client)
    token = obtener_token(client)

    respuesta = client.post(
        "/auth/logout",
        headers=cabecera_token(token)
    )

    assert respuesta.status_code == 200

    # Un token revocado no debe permitir consultar el perfil.
    respuesta_perfil = client.get(
        "/users/me",
        headers=cabecera_token(token)
    )

    assert respuesta_perfil.status_code == 401


def test_logout_sin_token(client):
    respuesta = client.post("/auth/logout")

    assert respuesta.status_code in (401, 403)


def test_token_invalido(client):
    respuesta = client.get(
        "/users/me",
        headers=cabecera_token("token-invalido")
    )

    assert respuesta.status_code == 401


def test_recuperacion_correo_inexistente(client):
    respuesta = client.post(
        "/auth/reset-password",
        json={
            "email": "noexiste@subsonic.com"
        }
    )

    assert respuesta.status_code == 200


def test_recuperacion_sin_smtp(client):
    registrar_usuario(client)

    respuesta = client.post(
        "/auth/reset-password",
        json={
            "email": USUARIO["email"]
        }
    )

    # Sin SMTP configurado, no debe simular un envio.
    assert respuesta.status_code == 503


def test_confirmacion_token_invalido(client):
    respuesta = client.post(
        "/auth/reset-password/confirm",
        json={
            "token": "token-que-no-existe",
            "new_password": "NuevaContrasena123!"
        }
    )

    assert respuesta.status_code == 400


def test_recuperacion_completa(client, monkeypatch):
    registrar_usuario(client)

    # Simulamos el envio del correo sin enviar mensajes reales.
    token_enviado = []

    def simular_correo(destinatario, token):
        token_enviado.append(token)

    monkeypatch.setattr(
        "openapi_server.auth_flows.enviar_correo_recuperacion",
        simular_correo
    )

    solicitud = client.post(
        "/auth/reset-password",
        json={
            "email": USUARIO["email"]
        }
    )

    assert solicitud.status_code == 200
    assert len(token_enviado) == 1

    token = token_enviado[0]

    # Se debe almacenar el hash, no el token original.
    with SessionLocal() as db:
        registro = db.get(
            PasswordResetDB,
            hash_token(token)
        )

        assert registro is not None

    nueva_password = "NuevaContrasena123!"

    confirmacion = client.post(
        "/auth/reset-password/confirm",
        json={
            "token": token,
            "new_password": nueva_password
        }
    )

    assert confirmacion.status_code == 200

    # La contrasena antigua deja de funcionar.
    login_antiguo = iniciar_sesion(client)

    assert login_antiguo.status_code == 401

    # La nueva contrasena permite iniciar sesion.
    login_nuevo = iniciar_sesion(
        client,
        password=nueva_password
    )

    assert login_nuevo.status_code == 200

    # El enlace no puede utilizarse dos veces.
    reutilizacion = client.post(
        "/auth/reset-password/confirm",
        json={
            "token": token,
            "new_password": "OtraContrasena123!"
        }
    )

    assert reutilizacion.status_code == 400


def test_recuperacion_invalida_sesiones_anteriores(
    client,
    monkeypatch
):
    # Registrar usuario e iniciar sesion
    registrar_usuario(client)
    token_antiguo = obtener_token(client)

    # Simular el envio del correo
    tokens_enviados = []

    def simular_correo(destinatario, token):
        tokens_enviados.append(token)

    monkeypatch.setattr(
        "openapi_server.auth_flows.enviar_correo_recuperacion",
        simular_correo
    )

    # Solicitar recuperacion
    respuesta = client.post(
        "/auth/reset-password",
        json={"email": USUARIO["email"]}
    )

    assert respuesta.status_code == 200
    assert len(tokens_enviados) == 1

    # Confirmar nueva contrasena
    confirmacion = client.post(
        "/auth/reset-password/confirm",
        json={
            "token": tokens_enviados[0],
            "new_password": "NuevaContrasena123!"
        }
    )

    assert confirmacion.status_code == 200

    # El JWT anterior debe quedar invalidado
    respuesta_antigua = client.get(
        "/users/me",
        headers=cabecera_token(token_antiguo)
    )

    assert respuesta_antigua.status_code == 401

    # La nueva contrasena debe permitir iniciar sesion
    respuesta_nueva = iniciar_sesion(
        client,
        password="NuevaContrasena123!"
    )

    assert respuesta_nueva.status_code == 200


def test_limite_recuperacion_60_segundos(
    client,
    monkeypatch
):
    registrar_usuario(client)

    correos_enviados = []

    def simular_correo(destinatario, token):
        correos_enviados.append(token)

    monkeypatch.setattr(
        "openapi_server.auth_flows.enviar_correo_recuperacion",
        simular_correo
    )

    # Primera solicitud
    primera = client.post(
        "/auth/reset-password",
        json={"email": USUARIO["email"]}
    )

    # Segunda solicitud inmediatamente despues
    segunda = client.post(
        "/auth/reset-password",
        json={"email": USUARIO["email"]}
    )

    assert primera.status_code == 200
    assert segunda.status_code == 200

    # Solo debe generarse un correo
    assert len(correos_enviados) == 1

def test_dos_logins_generan_tokens_diferentes(client):
    registrar_usuario(client)

    primer_login = iniciar_sesion(client)
    segundo_login = iniciar_sesion(client)

    assert primer_login.status_code == 200
    assert segundo_login.status_code == 200

    primer_token = primer_login.json()["access_token"]
    segundo_token = segundo_login.json()["access_token"]

    assert primer_token != segundo_token