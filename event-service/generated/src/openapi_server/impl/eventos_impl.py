
from typing import List
from uuid import uuid4

from fastapi import HTTPException

from openapi_server.apis.eventos_api_base import BaseEventosApi
from openapi_server.models.create_event_request import CreateEventRequest
from openapi_server.models.event import Event


# Almacenamiento temporal de eventos
eventos: List[Event] = []


class EventosApiImpl(BaseEventosApi):

    # GET /events
    # Devuelve todos los eventos registrados
    async def get_all_events(self) -> List[Event]:
        return eventos

    # POST /events
    # Crea un nuevo evento
    async def create_event(
        self,
        create_event_request: CreateEventRequest
    ) -> Event:

        # Validar las fechas
        if create_event_request.start_date > create_event_request.end_date:
            raise HTTPException(
                status_code=400,
                detail="La fecha de inicio no puede ser posterior a la fecha de fin"
            )

        # Generar un identificador unico
        nuevo_id = f"evt_{uuid4().hex}"

        # Crear el evento
        nuevo_evento = Event(
            id=nuevo_id,
            name=create_event_request.name,
            start_date=create_event_request.start_date,
            end_date=create_event_request.end_date,
            venue=create_event_request.venue,
            location_city=create_event_request.location_city
        )

        # Almacenar el evento
        eventos.append(nuevo_evento)

        return nuevo_evento

    # GET /events/{id}
    # Consulta un evento por su identificador
    async def get_event_by_id(self, id: str) -> Event:

        for evento in eventos:
            if evento.id == id:
                return evento

        raise HTTPException(
            status_code=404,
            detail="Evento no encontrado"
        )

    # PUT /events/{id}
    # Actualiza los datos de un evento existente
    async def update_event(
        self,
        id: str,
        create_event_request: CreateEventRequest
    ) -> Event:

        # Validar las fechas
        if create_event_request.start_date > create_event_request.end_date:
            raise HTTPException(
                status_code=400,
                detail="La fecha de inicio no puede ser posterior a la fecha de fin"
            )

        for indice, evento in enumerate(eventos):
            if evento.id == id:

                evento_actualizado = Event(
                    id=id,
                    name=create_event_request.name,
                    start_date=create_event_request.start_date,
                    end_date=create_event_request.end_date,
                    venue=create_event_request.venue,
                    location_city=create_event_request.location_city
                )

                eventos[indice] = evento_actualizado

                return evento_actualizado

        raise HTTPException(
            status_code=404,
            detail="Evento no encontrado"
        )

    # DELETE /events/{id}
    # Elimina un evento existente
    async def delete_event(self, id: str) -> None:

        for indice, evento in enumerate(eventos):
            if evento.id == id:
                eventos.pop(indice)
                return None

        raise HTTPException(
            status_code=404,
            detail="Evento no encontrado"
        )
