
from typing import List
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from openapi_server.apis.eventos_api_base import BaseEventosApi
from openapi_server.models.create_event_request import CreateEventRequest
from openapi_server.models.event import Event

from openapi_server.database import SessionLocal
from openapi_server.db_models import EventDB


class EventosApiImpl(BaseEventosApi):

    # GET /events
    # Obtener todos los festivales de PostgreSQL
    async def get_all_events(self) -> List[Event]:

        with SessionLocal() as db:
            eventos_db = db.scalars(
                select(EventDB)
            ).all()

            return [
                Event.model_validate(
                    evento,
                    from_attributes=True
                )
                for evento in eventos_db
            ]

    # POST /events
    # Crear un festival en PostgreSQL
    async def create_event(
        self,
        create_event_request: CreateEventRequest
    ) -> Event:

        if create_event_request.start_date > create_event_request.end_date:
            raise HTTPException(
                status_code=400,
                detail="La fecha de inicio no puede ser posterior a la fecha de fin"
            )

        nuevo_evento = EventDB(
            id=f"evt_{uuid4().hex}",
            name=create_event_request.name,
            start_date=create_event_request.start_date,
            end_date=create_event_request.end_date,
            venue=create_event_request.venue,
            location_city=create_event_request.location_city
        )

        with SessionLocal() as db:
            db.add(nuevo_evento)
            db.commit()
            db.refresh(nuevo_evento)

            return Event.model_validate(
                nuevo_evento,
                from_attributes=True
            )

    # GET /events/{id}
    # Consultar un festival por su identificador
    async def get_event_by_id(self, id: str) -> Event:

        with SessionLocal() as db:
            evento = db.get(EventDB, id)

            if evento is None:
                raise HTTPException(
                    status_code=404,
                    detail="Evento no encontrado"
                )

            return Event.model_validate(
                evento,
                from_attributes=True
            )

    # PUT /events/{id}
    # Actualizar un festival en PostgreSQL
    async def update_event(
        self,
        id: str,
        create_event_request: CreateEventRequest
    ) -> Event:

        if create_event_request.start_date > create_event_request.end_date:
            raise HTTPException(
                status_code=400,
                detail="La fecha de inicio no puede ser posterior a la fecha de fin"
            )

        with SessionLocal() as db:
            evento = db.get(EventDB, id)

            if evento is None:
                raise HTTPException(
                    status_code=404,
                    detail="Evento no encontrado"
                )

            evento.name = create_event_request.name
            evento.start_date = create_event_request.start_date
            evento.end_date = create_event_request.end_date
            evento.venue = create_event_request.venue
            evento.location_city = create_event_request.location_city

            db.commit()
            db.refresh(evento)

            return Event.model_validate(
                evento,
                from_attributes=True
            )

    # DELETE /events/{id}
    # Eliminar un festival de PostgreSQL
    async def delete_event(self, id: str) -> None:

        with SessionLocal() as db:
            evento = db.get(EventDB, id)

            if evento is None:
                raise HTTPException(
                    status_code=404,
                    detail="Evento no encontrado"
                )

            # Evitar eliminar eventos con datos relacionados.
            # Las relaciones se gestionarán después.
            from openapi_server.db_models import (
                ScheduleEntryDB,
                PassConfigDB,
                TicketDB
            )

            tiene_actuaciones = db.scalar(
                select(ScheduleEntryDB.id)
                .where(ScheduleEntryDB.event_id == id)
                .limit(1)
            )

            tiene_pases = db.scalar(
                select(PassConfigDB.id)
                .where(PassConfigDB.event_id == id)
                .limit(1)
            )

            tiene_entradas = db.scalar(
                select(TicketDB.id)
                .where(TicketDB.event_id == id)
                .limit(1)
            )

            if (
                tiene_actuaciones is not None
                or tiene_pases is not None
                or tiene_entradas is not None
            ):
                raise HTTPException(
                    status_code=409,
                    detail="No se puede eliminar un evento con actuaciones, pases o entradas asociados"
                )

            db.delete(evento)
            db.commit()

            return None
