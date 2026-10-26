
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select

from openapi_server.apis.presupuestos_y_solicitudes_api_base import (
    BasePresupuestosYSolicitudesApi
)
from openapi_server.models.create_space_proposal_request import (
    CreateSpaceProposalRequest
)
from openapi_server.models.space_proposal import SpaceProposal
from openapi_server.models.update_proposal_status_request import (
    UpdateProposalStatusRequest
)

from openapi_server.database import SessionLocal
from openapi_server.db_models import (
    ProviderDB,
    SpaceDB,
    SpaceProposalDB
)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def convertir_propuesta(
    propuesta: SpaceProposalDB
) -> SpaceProposal:

    return SpaceProposal(
        id=propuesta.id,
        space_id=propuesta.space_id,
        provider_id=propuesta.provider_id,
        event_id=propuesta.event_id,
        budget_proposal=float(propuesta.budget_proposal),
        setup_date=propuesta.setup_date,
        status=propuesta.status
    )


def validar_presupuesto(valor) -> Decimal:

    try:
        presupuesto = Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=400,
            detail="Presupuesto no valido"
        ) from exc

    if not presupuesto.is_finite() or presupuesto <= 0:
        raise HTTPException(
            status_code=400,
            detail="El presupuesto debe ser mayor que cero"
        )

    if presupuesto.as_tuple().exponent < -2:
        raise HTTPException(
            status_code=400,
            detail="El presupuesto admite como maximo dos decimales"
        )

    if presupuesto >= Decimal("10000000000"):
        raise HTTPException(
            status_code=400,
            detail="El presupuesto supera el limite permitido"
        )

    return presupuesto


def validar_solicitud(
    solicitud: CreateSpaceProposalRequest
) -> dict:

    espacio_id = solicitud.space_id.strip()
    proveedor_id = solicitud.provider_id.strip()
    evento_id = solicitud.event_id.strip()

    if not espacio_id:
        raise HTTPException(
            status_code=400,
            detail="El identificador del espacio es obligatorio"
        )

    if not proveedor_id:
        raise HTTPException(
            status_code=400,
            detail="El identificador del proveedor es obligatorio"
        )

    if not evento_id:
        raise HTTPException(
            status_code=400,
            detail="El identificador del evento es obligatorio"
        )

    return {
        "space_id": espacio_id,
        "provider_id": proveedor_id,
        "event_id": evento_id,
        "budget_proposal": validar_presupuesto(
            solicitud.budget_proposal
        ),
        "setup_date": solicitud.setup_date
    }


def comprobar_propietario(
    proveedor: ProviderDB,
    usuario_actual: dict
):
    if (
        proveedor.user_id != usuario_actual["id"]
        or usuario_actual["role"] != "provider"
    ):
        raise HTTPException(
            status_code=403,
            detail="No puedes presentar propuestas de otra empresa"
        )


def comprobar_acceso_proveedor(
    proveedor: ProviderDB,
    usuario_actual: dict
):
    if (
        usuario_actual["role"] != "admin"
        and proveedor.user_id != usuario_actual["id"]
    ):
        raise HTTPException(
            status_code=403,
            detail="No puedes consultar las propuestas de otra empresa"
        )


# ============================================================
# IMPLEMENTACION DE PRESUPUESTOS Y SOLICITUDES
# ============================================================

class PresupuestosYSolicitudesApiImpl(
    BasePresupuestosYSolicitudesApi
):

    # POST /requests
    async def create_space_proposal(
        self,
        create_space_proposal_request: CreateSpaceProposalRequest,
        usuario_actual: dict
    ) -> SpaceProposal:

        datos = validar_solicitud(
            create_space_proposal_request
        )

        with SessionLocal() as db:

            proveedor = db.get(
                ProviderDB,
                datos["provider_id"]
            )

            if proveedor is None:
                raise HTTPException(
                    status_code=404,
                    detail="Proveedor no encontrado"
                )

            comprobar_propietario(
                proveedor,
                usuario_actual
            )

            # Bloquear el espacio para coordinar
            # propuestas con adjudicaciones simultaneas.
            espacio = db.scalar(
                select(SpaceDB)
                .where(SpaceDB.id == datos["space_id"])
                .with_for_update()
            )

            if espacio is None:
                raise HTTPException(
                    status_code=404,
                    detail="Espacio no encontrado"
                )

            if espacio.event_id != datos["event_id"]:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "El espacio no pertenece "
                        "al evento indicado"
                    )
                )

            if not espacio.is_available:
                raise HTTPException(
                    status_code=409,
                    detail="El espacio ya no esta disponible"
                )

            # Evitar propuestas pendientes duplicadas
            # del mismo proveedor para el mismo espacio.
            existente = db.scalar(
                select(SpaceProposalDB.id)
                .where(
                    SpaceProposalDB.provider_id == datos["provider_id"],
                    SpaceProposalDB.space_id == datos["space_id"],
                    SpaceProposalDB.status == "pending"
                )
                .limit(1)
            )

            if existente is not None:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "El proveedor ya tiene una propuesta "
                        "pendiente para este espacio"
                    )
                )

            propuesta = SpaceProposalDB(
                id=f"req_{uuid4().hex}",
                space_id=datos["space_id"],
                provider_id=datos["provider_id"],
                event_id=datos["event_id"],
                budget_proposal=datos["budget_proposal"],
                setup_date=datos["setup_date"],
                status="pending"
            )

            db.add(propuesta)
            db.commit()
            db.refresh(propuesta)

            return convertir_propuesta(propuesta)

    # GET /requests/provider/{providerId}
    async def get_proposals_by_provider(
        self,
        providerId: str,
        usuario_actual: dict
    ) -> list[SpaceProposal]:

        with SessionLocal() as db:

            proveedor = db.get(
                ProviderDB,
                providerId
            )

            if proveedor is None:
                raise HTTPException(
                    status_code=404,
                    detail="Proveedor no encontrado"
                )

            comprobar_acceso_proveedor(
                proveedor,
                usuario_actual
            )

            propuestas = db.scalars(
                select(SpaceProposalDB)
                .where(
                    SpaceProposalDB.provider_id == providerId
                )
                .order_by(SpaceProposalDB.id)
            ).all()

            return [
                convertir_propuesta(propuesta)
                for propuesta in propuestas
            ]

    # GET /requests/event/{eventId}
    async def get_proposals_by_event(
        self,
        eventId: str
    ) -> list[SpaceProposal]:

        with SessionLocal() as db:

            propuestas = db.scalars(
                select(SpaceProposalDB)
                .where(
                    SpaceProposalDB.event_id == eventId
                )
                .order_by(SpaceProposalDB.id)
            ).all()

            return [
                convertir_propuesta(propuesta)
                for propuesta in propuestas
            ]

    # PUT /requests/{id}/status
    async def update_proposal_status(
        self,
        id: str,
        update_proposal_status_request: UpdateProposalStatusRequest
    ) -> None:

        nuevo_estado = update_proposal_status_request.status

        if hasattr(nuevo_estado, "value"):
            nuevo_estado = nuevo_estado.value

        if nuevo_estado not in {
            "pending",
            "approved",
            "rejected"
        }:
            raise HTTPException(
                status_code=400,
                detail="Estado de propuesta no valido"
            )

        with SessionLocal() as db:

            try:
                # Primero consultar la propuesta para
                # identificar el espacio que utiliza.
                propuesta_inicial = db.get(
                    SpaceProposalDB,
                    id
                )

                if propuesta_inicial is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Propuesta no encontrada"
                    )

                # Bloquear el espacio antes de adjudicar.
                # Todas las aprobaciones de este espacio
                # quedan serializadas en PostgreSQL.
                espacio = db.scalar(
                    select(SpaceDB)
                    .where(
                        SpaceDB.id == propuesta_inicial.space_id
                    )
                    .with_for_update()
                )

                if espacio is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Espacio no encontrado"
                    )

                # Bloquear tambien la propuesta y recargar
                # sus valores despues del bloqueo.
                propuesta = db.scalar(
                    select(SpaceProposalDB)
                    .where(SpaceProposalDB.id == id)
                    .with_for_update()
                    .execution_options(populate_existing=True)
                )

                if propuesta is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Propuesta no encontrada"
                    )

                estado_actual = propuesta.status

                # Repetir el mismo estado no tiene efectos.
                if nuevo_estado == estado_actual:
                    return None

                # Una propuesta resuelta es definitiva.
                if estado_actual != "pending":
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            "No se puede modificar "
                            "una propuesta ya resuelta"
                        )
                    )

                # Solo permitimos resolver propuestas:
                # pending -> approved
                # pending -> rejected
                if nuevo_estado == "pending":
                    raise HTTPException(
                        status_code=409,
                        detail="La propuesta ya esta pendiente"
                    )

                if nuevo_estado == "approved":

                    if not espacio.is_available:
                        raise HTTPException(
                            status_code=409,
                            detail=(
                                "El espacio ya esta adjudicado "
                                "o no esta disponible"
                            )
                        )

                    otra_aprobada = db.scalar(
                        select(SpaceProposalDB.id)
                        .where(
                            SpaceProposalDB.space_id == espacio.id,
                            SpaceProposalDB.status == "approved",
                            SpaceProposalDB.id != propuesta.id
                        )
                        .limit(1)
                    )

                    if otra_aprobada is not None:
                        raise HTTPException(
                            status_code=409,
                            detail=(
                                "Ya existe una propuesta aprobada "
                                "para este espacio"
                            )
                        )

                    propuesta.status = "approved"

                    # Reservar el espacio adjudicado.
                    espacio.is_available = False

                else:
                    propuesta.status = "rejected"

                db.commit()

                return None

            except Exception:
                db.rollback()
                raise
