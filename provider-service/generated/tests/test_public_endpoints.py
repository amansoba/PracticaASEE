
# ============================================================
# PRUEBAS DE ENDPOINTS PUBLICOS
# ============================================================

def test_listar_servicios_vacios(client):

    respuesta = client.get("/external-services")

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_listar_espacios_vacios(client):

    respuesta = client.get(
        "/spaces",
        params={"event_id": "evt_001"}
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_espacios_requieren_evento(client):

    respuesta = client.get("/spaces")

    assert respuesta.status_code == 422


# ============================================================
# PRUEBAS DE ACCESO NO AUTORIZADO
# ============================================================

def test_listar_proveedores_sin_token(client):

    respuesta = client.get("/providers")

    assert respuesta.status_code == 401


def test_registrar_proveedor_sin_token(client):

    respuesta = client.post(
        "/providers",
        json={
            "user_id": "usr_001",
            "company_name": "Empresa de Sonido",
            "cif_nif": "B12345678",
            "service_category": "Sonido",
            "contact_email": "contacto@ejemplo.com"
        }
    )

    assert respuesta.status_code == 401


def test_consultar_propuestas_sin_token(client):

    respuesta = client.get(
        "/requests/event/evt_001"
    )

    assert respuesta.status_code == 401
