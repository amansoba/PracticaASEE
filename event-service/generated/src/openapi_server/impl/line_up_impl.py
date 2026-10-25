
from typing import List
from uuid import uuid4
from datetime import timezone
import os

import httpx
from fastapi import HTTPException
from sqlalchemy import select

from openapi_server.apis.line_up_api_base import BaseLineUpApi
from openapi_server.models.create_schedule_entry_request import CreateScheduleEntryRequest
from openapi_server.models.schedule_entry import ScheduleEntry

from openapi_server.database import SessionLocal
from openapi_server.db_models import EventDB, ScheduleEntryDB


class LineUpApiImpl(BaseLineUpApi):

    # GET /events/{id}/lineup
    # Consultar las actuaciones de un festival
    async def get_event_lineup(self, id: str) -> List[ScheduleEntry]:

        with SessionLocal() as db:

            # Comprobar que el festival existe
            evento = db.get(EventDB, id)

            if evento is None:
                raise HTTPException(
                    status_code=404,
                    detail="Evento no encontrado"
                )

            # Obtener las actuaciones desde PostgreSQL
            actuaciones_db = db.scalars(
                select(ScheduleEntryDB)
                .where(ScheduleEntryDB.event_id == id)
                .order_by(ScheduleEntryDB.start_time)
            ).all()

            # Convertir los registros a modelos de la API
            return [
                ScheduleEntry.model_validate(
                    actuacion,
                    from_attributes=True
                )
                for actuacion in actuaciones_db
            ]

    # POST /events/{id}/lineup
    # Añadir una nueva actuacion al festival
    async def add_schedule_entry(
        self,
        id: str,
        create_schedule_entry_request: CreateScheduleEntryRequest
    ) -> ScheduleEntry:

        inicio = create_schedule_entry_request.start_time
        fin = create_schedule_entry_request.end_time

        # Comprobar que las fechas incluyen zona horaria
        if (
            inicio.tzinfo is None
            or inicio.utcoffset() is None
            or fin.tzinfo is None
            or fin.utcoffset() is None
        ):
            raise HTTPException(
                status_code=400,
                detail="Las fechas deben incluir zona horaria"
            )

        # Comprobar que el inicio es anterior al fin
        if inicio >= fin:
            raise HTTPException(
                status_code=400,
                detail="La fecha de inicio debe ser anterior a la de fin"
            )

        # Normalizar las fechas a UTC
        inicio_utc = inicio.astimezone(timezone.utc)
        fin_utc = fin.astimezone(timezone.utc)

        with SessionLocal() as db:

            # Comprobar que el festival existe
            evento = db.get(EventDB, id)

            if evento is None:
                raise HTTPException(
                    status_code=404,
                    detail="Evento no encontrado"
                )

            # Comprobar que la actuacion pertenece
            # a las fechas del festival
            if (
                inicio_utc.date() < evento.start_date
                or fin_utc.date() > evento.end_date
            ):
                raise HTTPException(
                    status_code=400,
                    detail="La actuacion esta fuera de las fechas del festival"
                )

            # Obtener actuaciones del mismo festival
            actuaciones_existentes = db.scalars(
                select(ScheduleEntryDB)
                .where(ScheduleEntryDB.event_id == id)
            ).all()

            # Comprobar solapamientos en el mismo escenario
            for actuacion in actuaciones_existentes:

                mismo_escenario = (
                    actuacion.stage.casefold()
                    == create_schedule_entry_request.stage.casefold()
                )

                solapamiento = (
                    inicio_utc < actuacion.end_time
                    and fin_utc > actuacion.start_time
                )

                if mismo_escenario and solapamiento:
                    raise HTTPException(
                        status_code=400,
                        detail="Ya existe una actuacion en ese escenario y horario"
                    )

        # Comprobar que Catálogo Musical está configurado
        catalog_url = os.getenv("CATALOG_SERVICE_URL")

        if not catalog_url:
            raise HTTPException(
                status_code=503,
                detail="Catalogo Musical no esta configurado"
            )

        artist_id = create_schedule_entry_request.artist_id

        # Validar el artista mediante una consulta REST
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                respuesta = await client.get(
                    f"{catalog_url.rstrip('/')}/artists/{artist_id}"
                )

        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail="Catalogo Musical no esta disponible"
            )

        if respuesta.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="El artista no existe en Catalogo Musical"
            )

        if respuesta.status_code != 200:
            raise HTTPException(
                status_code=503,
                detail="No se pudo validar el artista"
            )

        # Crear la actuacion en PostgreSQL
        with SessionLocal() as db:

            nueva_actuacion = ScheduleEntryDB(
                id=f"sch_{uuid4().hex}",
                event_id=id,
                artist_id=artist_id,
                artist_name=create_schedule_entry_request.artist_name,
                stage=create_schedule_entry_request.stage,
                start_time=inicio_utc,
                end_time=fin_utc
            )

            db.add(nueva_actuacion)
            db.commit()
            db.refresh(nueva_actuacion)

            return ScheduleEntry.model_validate(
                nueva_actuacion,
                from_attributes=True
            )
