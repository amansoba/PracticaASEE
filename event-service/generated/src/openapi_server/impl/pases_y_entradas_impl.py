
from typing import List
from uuid import uuid4
from datetime import datetime, timezone
import os

import httpx
from fastapi import HTTPException
from sqlalchemy import select

from openapi_server.apis.pases_y_entradas_api_base import (
    BasePasesYEntradasApi
)
from openapi_server.models.create_pass_config_request import (
    CreatePassConfigRequest
)
from openapi_server.models.pass_config import PassConfig
from openapi_server.models.ticket_purchase_request import (
    TicketPurchaseRequest
)
from openapi_server.models.ticket import Ticket

from openapi_server.database import SessionLocal
from openapi_server.db_models import (
    EventDB,
    PassConfigDB,
    TicketDB
)


class PasesYEntradasApiImpl(BasePasesYEntradasApi):

    # GET /events/{id}/passes
    # Consultar los tipos de pase de un festival
    async def get_pass_configs_by_event(
        self,
        id: str
    ) -> List[PassConfig]:

        with SessionLocal() as db:

            evento = db.get(EventDB, id)

            if evento is None:
                raise HTTPException(
                    status_code=404,
                    detail="Evento no encontrado"
                )

            pases_db = db.scalars(
                select(PassConfigDB)
                .where(PassConfigDB.event_id == id)
            ).all()

            return [
                PassConfig.model_validate(
                    pase,
                    from_attributes=True
                )
                for pase in pases_db
            ]

    # POST /events/{id}/passes
    # Crear un nuevo tipo de pase en PostgreSQL
    async def create_pass_config(
        self,
        id: str,
        create_pass_config_request: CreatePassConfigRequest
    ) -> PassConfig:

        if create_pass_config_request.price < 0:
            raise HTTPException(
                status_code=400,
                detail="El precio no puede ser negativo"
            )

        if create_pass_config_request.capacity <= 0:
            raise HTTPException(
                status_code=400,
                detail="El aforo debe ser mayor que cero"
            )

        with SessionLocal() as db:

            evento = db.get(EventDB, id)

            if evento is None:
                raise HTTPException(
                    status_code=404,
                    detail="Evento no encontrado"
                )

            nuevo_pase = PassConfigDB(
                id=f"pass_{uuid4().hex}",
                event_id=id,
                type_name=create_pass_config_request.type_name,
                price=create_pass_config_request.price,
                capacity=create_pass_config_request.capacity,
                available_tickets=create_pass_config_request.capacity,
                benefits=create_pass_config_request.benefits or []
            )

            db.add(nuevo_pase)
            db.commit()
            db.refresh(nuevo_pase)

            return PassConfig.model_validate(
                nuevo_pase,
                from_attributes=True
            )

    # POST /tickets/purchase
    # Emitir una entrada y descontar el aforo
    async def purchase_ticket(
        self,
        ticket_purchase_request: TicketPurchaseRequest
    ) -> Ticket:

        event_id = ticket_purchase_request.event_id
        pass_id = ticket_purchase_request.pass_id
        user_id = ticket_purchase_request.user_id

        # Comprobar la existencia del evento y el pase
        with SessionLocal() as db:

            evento = db.get(EventDB, event_id)

            if evento is None:
                raise HTTPException(
                    status_code=404,
                    detail="Evento no encontrado"
                )

            pase = db.get(PassConfigDB, pass_id)

            if pase is None or pase.event_id != event_id:
                raise HTTPException(
                    status_code=404,
                    detail="Tipo de pase no encontrado"
                )

            if pase.available_tickets <= 0:
                raise HTTPException(
                    status_code=409,
                    detail="Aforo completo"
                )

        # Comprobar que auth-service esta configurado
        auth_url = os.getenv("AUTH_SERVICE_URL")

        if not auth_url:
            raise HTTPException(
                status_code=503,
                detail="Servicio de autenticacion no configurado"
            )

        # Verificar la existencia del comprador
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                respuesta = await client.get(
                    f"{auth_url.rstrip('/')}/users/{user_id}"
                )

        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail="Servicio de autenticacion no disponible"
            )

        if respuesta.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado"
            )

        if respuesta.status_code != 200:
            raise HTTPException(
                status_code=503,
                detail="No se pudo verificar el usuario"
            )

        # IMPORTANTE:
        # La integracion real con una pasarela de pagos
        # sigue pendiente. Esta emision es solo de desarrollo.

        # Transaccion para proteger el aforo en PostgreSQL
        with SessionLocal() as db:

            # Bloquear la fila del pase durante la compra
            pase = db.scalar(
                select(PassConfigDB)
                .where(
                    PassConfigDB.id == pass_id,
                    PassConfigDB.event_id == event_id
                )
                .with_for_update()
            )

            if pase is None:
                raise HTTPException(
                    status_code=404,
                    detail="Tipo de pase no encontrado"
                )

            # Volver a comprobar el aforo con la fila bloqueada
            if pase.available_tickets <= 0:
                raise HTTPException(
                    status_code=409,
                    detail="Aforo completo"
                )

            nueva_entrada = TicketDB(
                id=f"tck_{uuid4().hex}",
                event_id=event_id,
                pass_id=pass_id,
                user_id=user_id,
                qr_code=f"SUBSONIC-{uuid4().hex}",
                status="valid",
                purchased_at=datetime.now(timezone.utc)
            )

            # Guardar la entrada y descontar el aforo
            pase.available_tickets -= 1
            db.add(nueva_entrada)

            # Ambas operaciones se confirman juntas
            db.commit()
            db.refresh(nueva_entrada)

            return Ticket.model_validate(
                nueva_entrada,
                from_attributes=True
            )

    # GET /tickets/user/{userId}
    # Consultar las entradas de un usuario
    async def get_tickets_by_user(
        self,
        userId: str
    ) -> List[Ticket]:

        with SessionLocal() as db:

            entradas_db = db.scalars(
                select(TicketDB)
                .where(TicketDB.user_id == userId)
                .order_by(TicketDB.purchased_at.desc())
            ).all()

            return [
                Ticket.model_validate(
                    entrada,
                    from_attributes=True
                )
                for entrada in entradas_db
            ]
