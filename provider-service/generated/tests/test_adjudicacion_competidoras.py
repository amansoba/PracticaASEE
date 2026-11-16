
from openapi_server.main import app
from openapi_server.database import SessionLocal
from openapi_server.db_models import (
    ProviderDB,
    SpaceDB,
    SpaceProposalDB
)
from openapi_server.security_api import obtener_usuario_actual


def test_aprobar_propuesta_rechaza_competidoras(client):
    # Preparar dos empresas proveedoras.
    with SessionLocal() as db:
        db.add_all([
            ProviderDB(
                id="prov_001",
                user_id="usr_prov_001",
                company_name="Empresa de Sonido",
                cif_nif="B12345678",
                service_category="Sonido",
                contact_email="sonido@ejemplo.com"
            ),
            ProviderDB(
                id="prov_002",
                user_id="usr_prov_002",
                company_name="Empresa de Iluminacion",
                cif_nif="B87654321",
                service_category="Iluminacion",
                contact_email="luces@ejemplo.com"
            ),
            SpaceDB(
                id="spc_001",
                event_id="evt_001",
                name="Zona principal",
                base_price=1000,
                is_available=True
            ),
            SpaceDB(
                id="spc_002",
                event_id="evt_001",
                name="Zona secundaria",
                base_price=500,
                is_available=True
            )
        ])

        db.flush()

        # Dos propuestas para el mismo espacio.
        # Una tercera pertenece a un espacio diferente.
        db.add_all([
            SpaceProposalDB(
                id="req_001",
                space_id="spc_001",
                provider_id="prov_001",
                event_id="evt_001",
                budget_proposal=1500,
                status="pending"
            ),
            SpaceProposalDB(
                id="req_002",
                space_id="spc_001",
                provider_id="prov_002",
                event_id="evt_001",
                budget_proposal=1800,
                status="pending"
            ),
            SpaceProposalDB(
                id="req_003",
                space_id="spc_002",
                provider_id="prov_002",
                event_id="evt_001",
                budget_proposal=700,
                status="pending"
            )
        ])

        db.commit()

    # Simular un administrador autenticado.
    async def usuario_administrador():
        return {
            "id": "usr_admin_001",
            "role": "admin",
            "is_active": True
        }

    app.dependency_overrides[
        obtener_usuario_actual
    ] = usuario_administrador

    try:
        # Aprobar la primera propuesta.
        respuesta = client.put(
            "/requests/req_001/status",
            json={"status": "approved"}
        )

        assert respuesta.status_code == 200, respuesta.text

        # Comprobar los cambios en PostgreSQL.
        with SessionLocal() as db:
            aprobada = db.get(SpaceProposalDB, "req_001")
            competidora = db.get(SpaceProposalDB, "req_002")
            independiente = db.get(SpaceProposalDB, "req_003")

            espacio_adjudicado = db.get(SpaceDB, "spc_001")
            otro_espacio = db.get(SpaceDB, "spc_002")

            # La propuesta seleccionada queda aprobada.
            assert aprobada.status == "approved"

            # La propuesta competidora debe rechazarse.
            assert competidora.status == "rejected"

            # Las propuestas de otros espacios no cambian.
            assert independiente.status == "pending"

            # El espacio adjudicado deja de estar disponible.
            assert espacio_adjudicado.is_available is False

            # El otro espacio sigue disponible.
            assert otro_espacio.is_available is True

    finally:
        app.dependency_overrides.clear()
