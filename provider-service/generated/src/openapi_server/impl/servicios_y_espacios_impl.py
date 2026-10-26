
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from openapi_server.apis.servicios_y_espacios_api_base import (
    BaseServiciosYEspaciosApi
)

from openapi_server.models.create_external_service_request import (
    CreateExternalServiceRequest
)
from openapi_server.models.create_space_request import (
    CreateSpaceRequest
)
from openapi_server.models.external_service import ExternalService
from openapi_server.models.space import Space

from openapi_server.database import SessionLocal
from openapi_server.db_models import (
    ExternalServiceDB,
    SpaceDB
)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def convertir_servicio(
    servicio: ExternalServiceDB
) -> ExternalService:

    return ExternalService(
        id=servicio.id,
        name=servicio.name,
        description=servicio.description
    )


def convertir_espacio(
    espacio: SpaceDB
) -> Space:

    return Space(
        id=espacio.id,
        event_id=espacio.event_id,
        name=espacio.name,
        dimensions=espacio.dimensions,
        base_price=float(espacio.base_price),
        is_available=espacio.is_available
    )


def validar_servicio(
    solicitud: CreateExternalServiceRequest
) -> dict:

    nombre = solicitud.name.strip()

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre del servicio es obligatorio"
        )

    descripcion = solicitud.description

    if descripcion is not None:
        descripcion = descripcion.strip()

    return {
        "name": nombre,
        "description": descripcion
    }


def validar_espacio(
    solicitud: CreateSpaceRequest
) -> dict:

    evento_id = solicitud.event_id.strip()
    nombre = solicitud.name.strip()

    if not evento_id:
        raise HTTPException(
            status_code=400,
            detail="El identificador del evento es obligatorio"
        )

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre del espacio es obligatorio"
        )

    try:
        precio = Decimal(str(solicitud.base_price))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=400,
            detail="Precio del espacio no valido"
        ) from exc

    if not precio.is_finite() or precio < 0:
        raise HTTPException(
            status_code=400,
            detail="El precio no puede ser negativo"
        )

    if precio.as_tuple().exponent < -2:
        raise HTTPException(
            status_code=400,
            detail="El precio admite como maximo dos decimales"
        )

    if precio >= Decimal("10000000000"):
        raise HTTPException(
            status_code=400,
            detail="El precio supera el limite permitido"
        )

    dimensiones = solicitud.dimensions

    if dimensiones is not None:
        dimensiones = dimensiones.strip()

    disponible = solicitud.is_available

    if disponible is None:
        disponible = True

    return {
        "event_id": evento_id,
        "name": nombre,
        "dimensions": dimensiones,
        "base_price": precio,
        "is_available": disponible
    }


# ============================================================
# IMPLEMENTACION DE SERVICIOS Y ESPACIOS
# ============================================================

class ServiciosYEspaciosApiImpl(BaseServiciosYEspaciosApi):

    # GET /external-services
    async def get_external_services(
        self
    ) -> list[ExternalService]:

        with SessionLocal() as db:

            servicios = db.scalars(
                select(ExternalServiceDB)
                .order_by(
                    ExternalServiceDB.name,
                    ExternalServiceDB.id
                )
            ).all()

            return [
                convertir_servicio(servicio)
                for servicio in servicios
            ]

    # POST /external-services
    async def create_external_service(
        self,
        create_external_service_request: CreateExternalServiceRequest
    ) -> ExternalService:

        datos = validar_servicio(
            create_external_service_request
        )

        with SessionLocal() as db:

            servicio = ExternalServiceDB(
                id=f"srv_{uuid4().hex}",
                name=datos["name"],
                description=datos["description"]
            )

            db.add(servicio)
            db.commit()
            db.refresh(servicio)

            return convertir_servicio(servicio)

    # GET /spaces?event_id=...
    async def get_spaces_by_event(
        self,
        event_id: str
    ) -> list[Space]:

        if not event_id.strip():
            raise HTTPException(
                status_code=400,
                detail="El identificador del evento es obligatorio"
            )

        with SessionLocal() as db:

            espacios = db.scalars(
                select(SpaceDB)
                .where(
                    SpaceDB.event_id == event_id.strip()
                )
                .order_by(
                    SpaceDB.name,
                    SpaceDB.id
                )
            ).all()

            return [
                convertir_espacio(espacio)
                for espacio in espacios
            ]

    # POST /spaces
    async def create_space(
        self,
        create_space_request: CreateSpaceRequest
    ) -> Space:

        datos = validar_espacio(
            create_space_request
        )

        # La existencia del evento se verifica
        # en el controlador antes de llamar aqui.

        with SessionLocal() as db:

            existente = db.scalar(
                select(SpaceDB)
                .where(
                    SpaceDB.event_id == datos["event_id"],
                    SpaceDB.name == datos["name"]
                )
            )

            if existente is not None:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Ya existe un espacio con ese nombre "
                        "en el evento"
                    )
                )

            espacio = SpaceDB(
                id=f"spc_{uuid4().hex}",
                event_id=datos["event_id"],
                name=datos["name"],
                dimensions=datos["dimensions"],
                base_price=datos["base_price"],
                is_available=datos["is_available"]
            )

            db.add(espacio)

            try:
                db.commit()
            except IntegrityError as exc:
                db.rollback()

                raise HTTPException(
                    status_code=409,
                    detail="El espacio ya existe en este evento"
                ) from exc

            db.refresh(espacio)

            return convertir_espacio(espacio)
