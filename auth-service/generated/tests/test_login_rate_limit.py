
from datetime import datetime, timedelta, timezone

from openapi_server.database import SessionLocal
from openapi_server.login_rate_limit import (
    LoginRateLimitDB,
    clave_email
)


USUARIO = {
    "name": "Usuario Limite",
    "email": "limite@subsonic.com",
    "password": "PruebaSegura123!"
}


def registrar(client):
    respuesta = client.post(
        "/auth/register",
        json=USUARIO
    )

    assert respuesta.status_code == 201


def login(client, password, email=None):
    return client.post(
        "/auth/login",
        json={
            "email": email or USUARIO["email"],
            "password": password
        }
    )


def bloquear_cuenta(client):
    for _ in range(5):
        respuesta = login(
            client,
            "ContrasenaIncorrecta"
        )

        assert respuesta.status_code == 401


# ============================================================
# TEST 1 - CINCO FALLOS Y BLOQUEO DEL SEXTO
# ============================================================

def test_login_bloqueado_tras_cinco_fallos(client):
    registrar(client)
    bloquear_cuenta(client)

    respuesta = login(
        client,
        "ContrasenaIncorrecta"
    )

    assert respuesta.status_code == 429
    assert "Retry-After" in respuesta.headers


# ============================================================
# TEST 2 - NO PERMITIR LOGIN DURANTE BLOQUEO
# ============================================================

def test_password_correcta_no_elude_bloqueo(client):
    registrar(client)
    bloquear_cuenta(client)

    respuesta = login(
        client,
        USUARIO["password"]
    )

    assert respuesta.status_code == 429


# ============================================================
# TEST 3 - RECUPERAR ACCESO TRAS 15 MINUTOS
# ============================================================

def test_recuperar_acceso_tras_ventana(client):
    registrar(client)
    bloquear_cuenta(client)

    with SessionLocal() as db:
        registro = db.get(
            LoginRateLimitDB,
            clave_email(USUARIO["email"])
        )

        assert registro is not None

        registro.window_started_at = (
            datetime.now(timezone.utc)
            - timedelta(minutes=16)
        )

        db.commit()

    respuesta = login(
        client,
        USUARIO["password"]
    )

    assert respuesta.status_code == 200


# ============================================================
# TEST 4 - LOGIN CORRECTO REINICIA FALLOS
# ============================================================

def test_login_correcto_reinicia_contador(client):
    registrar(client)

    for _ in range(3):
        assert login(
            client,
            "ContrasenaIncorrecta"
        ).status_code == 401

    assert login(
        client,
        USUARIO["password"]
    ).status_code == 200

    for _ in range(3):
        assert login(
            client,
            "ContrasenaIncorrecta"
        ).status_code == 401

    with SessionLocal() as db:
        registro = db.get(
            LoginRateLimitDB,
            clave_email(USUARIO["email"])
        )

        assert registro is not None
        assert registro.failed_attempts == 3


# ============================================================
# TEST 5 - CUENTAS INDEPENDIENTES
# ============================================================

def test_bloqueo_no_afecta_a_otro_usuario(client):
    registrar(client)
    bloquear_cuenta(client)

    otro_usuario = {
        "name": "Otro Usuario",
        "email": "otro@subsonic.com",
        "password": "OtraContrasena123!"
    }

    registro = client.post(
        "/auth/register",
        json=otro_usuario
    )

    assert registro.status_code == 201

    respuesta = login(
        client,
        otro_usuario["password"],
        email=otro_usuario["email"]
    )

    assert respuesta.status_code == 200


# ============================================================
# TEST 6 - USUARIOS INEXISTENTES
# ============================================================

def test_login_inexistente_tambien_limitado(client):
    for _ in range(5):
        respuesta = login(
            client,
            "ContrasenaIncorrecta",
            email="inexistente@subsonic.com"
        )

        assert respuesta.status_code == 401

    respuesta = login(
        client,
        "ContrasenaIncorrecta",
        email="inexistente@subsonic.com"
    )

    assert respuesta.status_code == 429
