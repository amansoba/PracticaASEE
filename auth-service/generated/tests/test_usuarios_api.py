
from sqlalchemy import select

from openapi_server.database import SessionLocal
from openapi_server.db_models import UserDB


USUARIO = {
    "name": "Usuario Prueba",
    "email": "usuario@subsonic.com",
    "password": "PruebaSegura123!",
    "phone": "600123456"
}


def registrar_usuario(client, datos=None):
    respuesta = client.post(
        "/auth/register",
        json=datos or USUARIO
    )

    assert respuesta.status_code == 201

    return respuesta.json()


def obtener_token(client, datos=None):
    usuario = datos or USUARIO

    respuesta = client.post(
        "/auth/login",
        json={
            "email": usuario["email"],
            "password": usuario["password"]
        }
    )

    assert respuesta.status_code == 200

    return respuesta.json()["access_token"]


def cabecera(token):
    return {
        "Authorization": f"Bearer {token}"
    }


def convertir_en_admin(usuario_id):
    """
    Prepara un administrador exclusivamente en la
    base de datos de pruebas.
    """
    with SessionLocal() as db:
        usuario = db.get(UserDB, usuario_id)

        assert usuario is not None

        usuario.role = "admin"
        db.commit()


def crear_admin(client):
    usuario = registrar_usuario(client)

    convertir_en_admin(usuario["id"])

    # Login posterior al cambio para obtener JWT con rol admin.
    token = obtener_token(client)

    return usuario, token


def test_consultar_mi_perfil(client):
    registrar_usuario(client)
    token = obtener_token(client)

    respuesta = client.get(
        "/users/me",
        headers=cabecera(token)
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["email"] == USUARIO["email"]
    assert respuesta.json()["role"] == "client"


def test_consultar_perfil_sin_token(client):
    respuesta = client.get("/users/me")

    assert respuesta.status_code in (401, 403)


def test_actualizar_mi_perfil(client):
    registrar_usuario(client)
    token = obtener_token(client)

    respuesta = client.put(
        "/users/me",
        headers=cabecera(token),
        json={
            "name": "Nombre Actualizado",
            "phone": "611222333"
        }
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["name"] == "Nombre Actualizado"

    consulta = client.get(
        "/users/me",
        headers=cabecera(token)
    )

    assert consulta.status_code == 200
    assert consulta.json()["phone"] == "611222333"


def test_actualizar_nombre_vacio(client):
    registrar_usuario(client)
    token = obtener_token(client)

    respuesta = client.put(
        "/users/me",
        headers=cabecera(token),
        json={
            "name": "   "
        }
    )

    assert respuesta.status_code == 400


def test_cliente_no_puede_listar_usuarios(client):
    registrar_usuario(client)
    token = obtener_token(client)

    respuesta = client.get(
        "/users",
        headers=cabecera(token)
    )

    assert respuesta.status_code == 403


def test_admin_puede_listar_usuarios(client):
    _, token = crear_admin(client)

    respuesta = client.get(
        "/users",
        headers=cabecera(token)
    )

    assert respuesta.status_code == 200
    assert len(respuesta.json()) >= 1


def test_consultar_usuario_por_id(client):
    usuario = registrar_usuario(client)
    token = obtener_token(client)

    respuesta = client.get(
        f"/users/{usuario['id']}",
        headers=cabecera(token)
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == usuario["id"]


def test_consultar_usuario_inexistente(client):
    registrar_usuario(client)
    token = obtener_token(client)

    respuesta = client.get(
        "/users/usr_no_existe",
        headers=cabecera(token)
    )

    assert respuesta.status_code == 404


def test_cliente_no_puede_modificar_roles(client):
    usuario = registrar_usuario(client)
    token = obtener_token(client)

    respuesta = client.put(
        f"/users/{usuario['id']}/role",
        headers=cabecera(token),
        json={
            "role": "admin"
        }
    )

    assert respuesta.status_code == 403


def test_admin_puede_modificar_roles(client):
    _, token = crear_admin(client)

    nuevo_usuario = {
        "name": "Nuevo Proveedor",
        "email": "proveedor@subsonic.com",
        "password": "ProveedorSeguro123!",
        "phone": "699888777"
    }

    usuario = registrar_usuario(
        client,
        nuevo_usuario
    )

    respuesta = client.put(
        f"/users/{usuario['id']}/role",
        headers=cabecera(token),
        json={
            "role": "provider"
        }
    )

    assert respuesta.status_code == 200

    with SessionLocal() as db:
        usuario_db = db.get(
            UserDB,
            usuario["id"]
        )

        assert usuario_db.role == "provider"


def test_rol_desactualizado_invalida_token(client):
    usuario = registrar_usuario(client)
    token_antiguo = obtener_token(client)

    convertir_en_admin(usuario["id"])

    respuesta = client.get(
        "/users/me",
        headers=cabecera(token_antiguo)
    )

    assert respuesta.status_code == 401
