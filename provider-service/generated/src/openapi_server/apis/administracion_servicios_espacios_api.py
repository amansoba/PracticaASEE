
from fastapi import APIRouter, Body, Depends, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from openapi_server.database import SessionLocal
from openapi_server.db_models import (
    ExternalServiceDB,
    SpaceDB,
    SpaceProposalDB
)
from openapi_server.event_client import consultar_evento
from openapi_server.models.create_external_service_request import (
    CreateExternalServiceRequest
)
from openapi_server.models.create_space_request import (
    CreateSpaceRequest
)
from openapi_server.models.external_service import ExternalService
from openapi_server.models.space import Space
from openapi_server.security_api import obtener_administrador

from openapi_server.impl.servicios_y_espacios_impl import (
    convertir_servicio,
    convertir_espacio,
    validar_servicio,
    validar_espacio
)


router = APIRouter()


# ============================================================
# PUT /external-services/{id}
# ============================================================

@router.put(
    "/external-services/{id}",
    tags=["Servicios y Espacios"],
    summary="Actualizar un servicio externo",
    response_model=ExternalService,
    responses={
        400: {"description": "Datos invalidos"},
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        404: {"description": "Servicio no encontrado"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def actualizar_servicio(
    id: str = Path(...),
    solicitud: CreateExternalServiceRequest = Body(...),
    usuario: dict = Depends(obtener_administrador)
) -> ExternalService:

    datos = validar_servicio(solicitud)

    with SessionLocal() as db:
        servicio = db.get(ExternalServiceDB, id)

        if servicio is None:
            raise HTTPException(
                status_code=404,
                detail="Servicio externo no encontrado"
            )

        servicio.name = datos["name"]
        servicio.description = datos["description"]

        db.commit()
        db.refresh(servicio)

        return convertir_servicio(servicio)


# ============================================================
# DELETE /external-services/{id}
# ============================================================

@router.delete(
    "/external-services/{id}",
    tags=["Servicios y Espacios"],
    summary="Eliminar un servicio externo",
    status_code=204,
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        404: {"description": "Servicio no encontrado"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def eliminar_servicio(
    id: str = Path(...),
    usuario: dict = Depends(obtener_administrador)
) -> None:

    with SessionLocal() as db:
        servicio = db.get(ExternalServiceDB, id)

        if servicio is None:
            raise HTTPException(
                status_code=404,
                detail="Servicio externo no encontrado"
            )

        db.delete(servicio)
        db.commit()

    return None


# ============================================================
# PUT /spaces/{id}
# ============================================================

@router.put(
    "/spaces/{id}",
    tags=["Servicios y Espacios"],
    summary="Actualizar un espacio",
    response_model=Space,
    responses={
        400: {"description": "Datos invalidos"},
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        404: {"description": "Espacio o evento no encontrado"},
        409: {"description": "Conflicto con espacios o propuestas"},
        503: {"description": "Servicio externo no disponible"}
    }
)
async def actualizar_espacio(
    id: str = Path(...),
    solicitud: CreateSpaceRequest = Body(...),
    usuario: dict = Depends(obtener_administrador)
) -> Space:

    datos = validar_espacio(solicitud)

    # Comprobar primero que existe el espacio.
    with SessionLocal() as db:
        if db.get(SpaceDB, id) is None:
            raise HTTPException(
                status_code=404,
                detail="Espacio no encontrado"
            )

    # Comprobar la existencia del evento en event-service.
    await consultar_evento(datos["event_id"])

    with SessionLocal() as db:
        espacio = db.scalar(
            select(SpaceDB)
            .where(SpaceDB.id == id)
            .with_for_update()
        )

        if espacio is None:
            raise HTTPException(
                status_code=404,
                detail="Espacio no encontrado"
            )

        propuestas = db.scalars(
            select(SpaceProposalDB)
            .where(SpaceProposalDB.space_id == id)
        ).all()

        # Las propuestas existentes pertenecen al
        # evento original y no pueden trasladarse.
        if (
            propuestas
            and espacio.event_id != datos["event_id"]
        ):
            raise HTTPException(
                status_code=409,
                detail=(
                    "No se puede cambiar el evento "
                    "de un espacio con propuestas"
                )
            )

        # Un espacio adjudicado no puede volver
        # a estar disponible mediante esta operacion.
        if datos["is_available"] and any(
            propuesta.status == "approved"
            for propuesta in propuestas
        ):
            raise HTTPException(
                status_code=409,
                detail=(
                    "Un espacio adjudicado "
                    "no puede marcarse como disponible"
                )
            )

        duplicado = db.scalar(
            select(SpaceDB.id)
            .where(
                SpaceDB.event_id == datos["event_id"],
                SpaceDB.name == datos["name"],
                SpaceDB.id != id
            )
        )

        if duplicado is not None:
            raise HTTPException(
                status_code=409,
                detail="Ya existe otro espacio con ese nombre"
            )

        espacio.event_id = datos["event_id"]
        espacio.name = datos["name"]
        espacio.dimensions = datos["dimensions"]
        espacio.base_price = datos["base_price"]
        espacio.is_available = datos["is_available"]

        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Ya existe otro espacio con ese nombre"
            ) from exc

        db.refresh(espacio)

        return convertir_espacio(espacio)


# ============================================================
# DELETE /spaces/{id}
# ============================================================

@router.delete(
    "/spaces/{id}",
    tags=["Servicios y Espacios"],
    summary="Eliminar un espacio",
    status_code=204,
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        404: {"description": "Espacio no encontrado"},
        409: {"description": "El espacio tiene propuestas"},
        503: {"description": "Autenticacion no disponible"}
    }
)
async def eliminar_espacio(
    id: str = Path(...),
    usuario: dict = Depends(obtener_administrador)
) -> None:

    with SessionLocal() as db:
        espacio = db.scalar(
            select(SpaceDB)
            .where(SpaceDB.id == id)
            .with_for_update()
        )

        if espacio is None:
            raise HTTPException(
                status_code=404,
                detail="Espacio no encontrado"
            )

        propuesta = db.scalar(
            select(SpaceProposalDB.id)
            .where(SpaceProposalDB.space_id == id)
            .limit(1)
        )

        if propuesta is not None:
            raise HTTPException(
                status_code=409,
                detail=(
                    "No se puede eliminar un espacio "
                    "que tiene propuestas asociadas"
                )
            )

        db.delete(espacio)

        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="El espacio tiene datos relacionados"
            ) from exc

    return None
