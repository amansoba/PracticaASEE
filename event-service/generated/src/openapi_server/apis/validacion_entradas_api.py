
from fastapi import APIRouter, Body, Security
from pydantic import BaseModel, Field

from openapi_server.models.ticket import Ticket
from openapi_server.models.extra_models import TokenModel
from openapi_server.security_api import get_token_BearerAuth
from openapi_server.impl.validacion_entradas_impl import (
    validar_entrada_qr
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter()


# ============================================================
# MODELO DE SOLICITUD
# ============================================================

class ValidarEntradaRequest(BaseModel):
    qr_code: str = Field(
        description="Codigo QR de la entrada"
    )


# ============================================================
# POST /tickets/validate
# ============================================================

@router.post(
    "/tickets/validate",
    tags=["Pases y Entradas"],
    summary="Validar una entrada mediante QR",
    response_model=Ticket,
    status_code=200,
    responses={
        400: {"description": "Codigo QR incorrecto"},
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere administrador"},
        404: {"description": "Entrada no encontrada"},
        409: {
            "description": "Entrada utilizada o cancelada"
        },
        503: {
            "description": "Autenticacion no disponible"
        }
    }
)
async def validate_ticket(
    solicitud: ValidarEntradaRequest = Body(...),
    usuario: TokenModel = Security(
        get_token_BearerAuth
    )
) -> Ticket:

    return validar_entrada_qr(
        solicitud.qr_code
    )
