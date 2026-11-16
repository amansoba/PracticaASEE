
from fastapi import HTTPException
from sqlalchemy import select

from openapi_server.database import SessionLocal
from openapi_server.db_models import TicketDB
from openapi_server.models.ticket import Ticket


def validar_entrada_qr(qr_code: str) -> Ticket:
    """
    Valida una entrada y la marca como utilizada.

    El bloqueo de PostgreSQL impide que dos
    validaciones simultaneas utilicen el mismo QR.
    """

    codigo = qr_code.strip()

    if not codigo or len(codigo) > 200:
        raise HTTPException(
            status_code=400,
            detail="Codigo QR no valido"
        )

    with SessionLocal() as db:
        try:
            entrada = db.scalar(
                select(TicketDB)
                .where(TicketDB.qr_code == codigo)
                .with_for_update()
            )

            if entrada is None:
                raise HTTPException(
                    status_code=404,
                    detail="Entrada no encontrada"
                )

            if entrada.status == "used":
                raise HTTPException(
                    status_code=409,
                    detail="La entrada ya ha sido utilizada"
                )

            if entrada.status == "cancelled":
                raise HTTPException(
                    status_code=409,
                    detail="La entrada esta cancelada"
                )

            if entrada.status != "valid":
                raise HTTPException(
                    status_code=409,
                    detail="La entrada no puede validarse"
                )

            entrada.status = "used"

            db.commit()
            db.refresh(entrada)

            return Ticket.model_validate(
                entrada,
                from_attributes=True
            )

        except Exception:
            db.rollback()
            raise
