
from datetime import datetime, timedelta, timezone
from hashlib import sha256

from fastapi import HTTPException
from sqlalchemy import DateTime, Integer, String, delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Mapped, mapped_column

from openapi_server.database import SessionLocal
from openapi_server.db_models import Base


MAX_INTENTOS = 5
VENTANA_MINUTOS = 15


class LoginRateLimitDB(Base):
    __tablename__ = "login_rate_limits"

    email_hash: Mapped[str] = mapped_column(
        String(64),
        primary_key=True
    )

    failed_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    window_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )


def ahora():
    return datetime.now(timezone.utc)


def normalizar_fecha(fecha):
    if fecha.tzinfo is None:
        return fecha.replace(tzinfo=timezone.utc)
    return fecha.astimezone(timezone.utc)


def clave_email(email):
    return sha256(
        email.strip().lower().encode("utf-8")
    ).hexdigest()


def comprobar_limite_login(email):
    """
    Rechaza temporalmente nuevos intentos si
    se han acumulado cinco fallos recientes.
    """

    with SessionLocal() as db:
        registro = db.get(
            LoginRateLimitDB,
            clave_email(email)
        )

        if registro is None:
            return

        fecha_inicio = normalizar_fecha(
            registro.window_started_at
        )

        transcurrido = ahora() - fecha_inicio

        if transcurrido >= timedelta(
            minutes=VENTANA_MINUTOS
        ):
            return

        if registro.failed_attempts >= MAX_INTENTOS:
            restante = (
                timedelta(minutes=VENTANA_MINUTOS)
                - transcurrido
            )

            segundos = max(
                1,
                int(restante.total_seconds()) + 1
            )

            raise HTTPException(
                status_code=429,
                detail=(
                    "Demasiados intentos de inicio "
                    "de sesion. Intentalo mas tarde."
                ),
                headers={
                    "Retry-After": str(segundos)
                }
            )


def registrar_intento_fallido(email):
    """
    Registra un fallo de autenticacion.

    La insercion y el bloqueo de fila evitan
    perder incrementos simultaneos.
    """

    identificador = clave_email(email)
    momento = ahora()

    with SessionLocal() as db:
        try:
            sentencia = insert(
                LoginRateLimitDB
            ).values(
                email_hash=identificador,
                failed_attempts=0,
                window_started_at=momento
            ).on_conflict_do_nothing(
                index_elements=["email_hash"]
            )

            db.execute(sentencia)

            registro = db.scalar(
                select(LoginRateLimitDB)
                .where(
                    LoginRateLimitDB.email_hash
                    == identificador
                )
                .with_for_update()
            )

            fecha_inicio = normalizar_fecha(
                registro.window_started_at
            )

            if (
                momento - fecha_inicio
                >= timedelta(minutes=VENTANA_MINUTOS)
            ):
                registro.failed_attempts = 0
                registro.window_started_at = momento

            registro.failed_attempts += 1

            db.commit()

        except Exception:
            db.rollback()
            raise


def reiniciar_intentos_login(email):
    """
    Elimina los fallos anteriores cuando
    el usuario inicia sesion correctamente.
    """

    with SessionLocal() as db:
        db.execute(
            delete(LoginRateLimitDB)
            .where(
                LoginRateLimitDB.email_hash
                == clave_email(email)
            )
        )

        db.commit()
