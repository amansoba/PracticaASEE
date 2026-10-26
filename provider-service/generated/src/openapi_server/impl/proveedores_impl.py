
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from openapi_server.apis.proveedores_api_base import (
    BaseProveedoresApi
)
from openapi_server.models.create_provider_request import (
    CreateProviderRequest
)
from openapi_server.models.provider_profile import ProviderProfile

from openapi_server.database import SessionLocal
from openapi_server.db_models import ProviderDB


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def convertir_proveedor(proveedor: ProviderDB) -> ProviderProfile:
    return ProviderProfile(
        id=proveedor.id,
        user_id=proveedor.user_id,
        company_name=proveedor.company_name,
        cif_nif=proveedor.cif_nif,
        service_category=proveedor.service_category,
        contact_email=proveedor.contact_email
    )


def validar_proveedor(solicitud: CreateProviderRequest) -> dict:
    campos = {
        "user_id": solicitud.user_id,
        "company_name": solicitud.company_name,
        "cif_nif": solicitud.cif_nif,
        "service_category": solicitud.service_category,
        "contact_email": str(solicitud.contact_email)
    }

    for nombre, valor in campos.items():
        if not isinstance(valor, str) or not valor.strip():
            raise HTTPException(
                status_code=400,
                detail=f"El campo {nombre} es obligatorio"
            )

    return {
        "user_id": campos["user_id"].strip(),
        "company_name": campos["company_name"].strip(),
        "cif_nif": campos["cif_nif"].strip().upper(),
        "service_category": campos["service_category"].strip(),
        "contact_email": campos["contact_email"].strip().lower()
    }


# ============================================================
# IMPLEMENTACION DE PROVEEDORES
# ============================================================

class ProveedoresApiImpl(BaseProveedoresApi):

    # GET /providers
    async def get_providers(self) -> list[ProviderProfile]:

        with SessionLocal() as db:
            proveedores = db.scalars(
                select(ProviderDB).order_by(
                    ProviderDB.company_name,
                    ProviderDB.id
                )
            ).all()

            return [
                convertir_proveedor(proveedor)
                for proveedor in proveedores
            ]

    # POST /providers
    async def create_provider(
        self,
        create_provider_request: CreateProviderRequest
    ) -> ProviderProfile:

        datos = validar_proveedor(create_provider_request)

        with SessionLocal() as db:
            usuario_existente = db.scalar(
                select(ProviderDB)
                .where(ProviderDB.user_id == datos["user_id"])
            )

            if usuario_existente is not None:
                raise HTTPException(
                    status_code=409,
                    detail="El usuario ya tiene una empresa registrada"
                )

            cif_existente = db.scalar(
                select(ProviderDB)
                .where(ProviderDB.cif_nif == datos["cif_nif"])
            )

            if cif_existente is not None:
                raise HTTPException(
                    status_code=409,
                    detail="Ya existe una empresa con ese CIF/NIF"
                )

            proveedor = ProviderDB(
                id=f"prov_{uuid4().hex}",
                user_id=datos["user_id"],
                company_name=datos["company_name"],
                cif_nif=datos["cif_nif"],
                service_category=datos["service_category"],
                contact_email=datos["contact_email"]
            )

            db.add(proveedor)

            try:
                db.commit()
            except IntegrityError as exc:
                db.rollback()
                raise HTTPException(
                    status_code=409,
                    detail="Ya existe una empresa con esos datos"
                ) from exc

            db.refresh(proveedor)

            return convertir_proveedor(proveedor)

    # GET /providers/{id}
    async def get_provider_by_id(
        self,
        id: str
    ) -> ProviderProfile:

        with SessionLocal() as db:
            proveedor = db.get(ProviderDB, id)

            if proveedor is None:
                raise HTTPException(
                    status_code=404,
                    detail="Proveedor no encontrado"
                )

            return convertir_proveedor(proveedor)
