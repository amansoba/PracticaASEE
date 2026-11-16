
import hashlib
import os
import secrets
import smtplib

from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, String, select
from sqlalchemy.orm import Mapped, mapped_column

from openapi_server.database import SessionLocal, engine
from openapi_server.db_models import Base, UserDB
from openapi_server.auth_security import (
    cifrar_password,
    verificar_token
)


# ============================================================
# MODELOS DE BASE DE DATOS
# ============================================================

class RevokedTokenDB(Base):
    __tablename__ = "revoked_tokens"

    token_hash: Mapped[str] = mapped_column(
        String(64),
        primary_key=True
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )


class PasswordResetDB(Base):
    __tablename__ = "password_resets"

    token_hash: Mapped[str] = mapped_column(
        String(64),
        primary_key=True
    )

    user_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("users.id"),
        nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )


class UserTokenInvalidationDB(Base):
    __tablename__ = "user_token_invalidations"

    user_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("users.id"),
        primary_key=True
    )

    invalid_before: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )


# ============================================================
# CREACION DE TABLAS
# ============================================================

def crear_tablas_auth():
    Base.metadata.create_all(
        bind=engine,
        tables=[
            RevokedTokenDB.__table__,
            PasswordResetDB.__table__,
            UserTokenInvalidationDB.__table__
        ]
    )


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def ahora() -> datetime:
    return datetime.now(timezone.utc)


def fecha_utc(fecha: datetime) -> datetime:
    """
    Normaliza fechas recibidas de PostgreSQL.
    """
    if fecha.tzinfo is None:
        return fecha.replace(tzinfo=timezone.utc)

    return fecha.astimezone(timezone.utc)


def hash_token(token: str) -> str:
    """
    Calcula un hash SHA-256 del token para no guardar
    el token original en PostgreSQL.
    """
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


# ============================================================
# REVOCACION DE TOKENS JWT
# ============================================================

def token_revocado(token: str) -> bool:
    """
    Comprueba si un JWT ha sido revocado al cerrar sesion.
    """
    with SessionLocal() as db:
        registro = db.get(
            RevokedTokenDB,
            hash_token(token)
        )

        return registro is not None


def token_usuario_invalidado(payload: dict) -> bool:
    """
    Comprueba si un JWT fue emitido antes de que
    el usuario restableciera su contrasena.
    """
    usuario_id = payload["sub"]

    emitido_en = datetime.fromtimestamp(
        payload["iat"],
        tz=timezone.utc
    )

    with SessionLocal() as db:
        registro = db.get(
            UserTokenInvalidationDB,
            usuario_id
        )

        if registro is None:
            return False

        # JWT iat has second precision. Keep equality invalidated so a token
        # issued in the reset second cannot escape revocation.
        return emitido_en <= fecha_utc(
            registro.invalid_before
        )


def cerrar_sesion(token: str) -> dict:
    """
    Revoca el JWT actual para impedir su reutilizacion.
    """
    payload = verificar_token(token)

    expiracion = datetime.fromtimestamp(
        payload["exp"],
        tz=timezone.utc
    )

    with SessionLocal() as db:
        identificador = hash_token(token)

        registro = db.get(
            RevokedTokenDB,
            identificador
        )

        if registro is None:
            db.add(
                RevokedTokenDB(
                    token_hash=identificador,
                    expires_at=expiracion
                )
            )

            db.commit()

    return {
        "message": "Sesion cerrada correctamente"
    }


# ============================================================
# ENVIO DEL CORREO DE RECUPERACION
# ============================================================

def enviar_correo_recuperacion(
    destinatario: str,
    token: str
):
    """
    Envia un enlace de recuperacion por SMTP.

    Requiere configurar las variables SMTP en .env.
    """
    servidor = os.getenv("SMTP_HOST")
    puerto = int(os.getenv("SMTP_PORT", "587"))
    usuario = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    remitente = os.getenv("SMTP_FROM")
    url_base = os.getenv("PASSWORD_RESET_URL")

    if not all([
        servidor,
        usuario,
        password,
        remitente,
        url_base
    ]):
        raise HTTPException(
            status_code=503,
            detail="Servicio de correo no configurado"
        )

    separador = "&" if "?" in url_base else "?"

    enlace = (
        f"{url_base}{separador}"
        f"{urlencode({'token': token})}"
    )

    mensaje = EmailMessage()
    mensaje["Subject"] = (
        "Subsonic - Recuperar contrasena"
    )
    mensaje["From"] = remitente
    mensaje["To"] = destinatario

    mensaje.set_content(
        "Has solicitado recuperar tu contrasena.\n\n"
        f"Abre este enlace:\n{enlace}\n\n"
        "El enlace caduca en 15 minutos.\n"
        "Si no has solicitado el cambio, ignora este correo."
    )

    try:
        if puerto == 465:
            with smtplib.SMTP_SSL(
                servidor,
                puerto,
                timeout=15
            ) as smtp:
                smtp.login(usuario, password)
                smtp.send_message(mensaje)

        else:
            with smtplib.SMTP(
                servidor,
                puerto,
                timeout=15
            ) as smtp:
                smtp.starttls()
                smtp.login(usuario, password)
                smtp.send_message(mensaje)

    except (OSError, smtplib.SMTPException) as exc:
        raise HTTPException(
            status_code=503,
            detail="No se ha podido enviar el correo"
        ) from exc


# ============================================================
# SOLICITUD DE RECUPERACION DE CONTRASENA
# ============================================================

def solicitar_recuperacion(email: str) -> dict:
    """
    Genera un token de recuperacion y envia un correo.

    Limita las solicitudes a una cada 60 segundos
    por usuario registrado.
    """
    email = email.strip().lower()

    respuesta = {
        "message": (
            "Si existe una cuenta con ese correo, "
            "recibira instrucciones de recuperacion"
        )
    }

    with SessionLocal() as db:
        usuario = db.scalar(
            select(UserDB).where(
                UserDB.email == email
            )
        )

        # No revelar si existe una cuenta con ese correo
        if usuario is None:
            return respuesta

        # Buscar la ultima solicitud del usuario
        ultima_solicitud = db.scalar(
            select(PasswordResetDB)
            .where(
                PasswordResetDB.user_id == usuario.id
            )
            .order_by(
                PasswordResetDB.expires_at.desc()
            )
            .limit(1)
        )

        # Limitar las solicitudes a una cada 60 segundos
        if ultima_solicitud is not None:
            fecha_solicitud = (
                fecha_utc(
                    ultima_solicitud.expires_at
                ) - timedelta(minutes=15)
            )

            if (
                ahora() - fecha_solicitud
                < timedelta(seconds=60)
            ):
                return respuesta

        # Generar un token aleatorio seguro
        token = secrets.token_urlsafe(32)

        # Guardar solamente su hash
        recuperacion = PasswordResetDB(
            token_hash=hash_token(token),
            user_id=usuario.id,
            expires_at=ahora() + timedelta(minutes=15)
        )

        db.add(recuperacion)
        db.flush()

        # Enviar el correo antes de confirmar la transaccion.
        # Si el correo falla, no se guarda el token.
        enviar_correo_recuperacion(
            usuario.email,
            token
        )

        db.commit()

    return respuesta


# ============================================================
# CONFIRMACION DE RECUPERACION
# ============================================================

class ConfirmarPasswordRequest(BaseModel):
    token: str = Field(
        min_length=1
    )

    new_password: str = Field(
        min_length=8
    )


router = APIRouter()


@router.post(
    "/auth/reset-password/confirm",
    tags=["Autenticacion"],
    summary="Confirmar recuperacion de contrasena"
)
async def confirmar_recuperacion(
    solicitud: ConfirmarPasswordRequest
):
    """
    Verifica el token de recuperacion y cambia la
    contrasena del usuario.

    El token solo puede utilizarse una vez.
    """
    identificador = hash_token(solicitud.token)

    with SessionLocal() as db:
        recuperacion = db.scalar(
            select(PasswordResetDB)
            .where(
                PasswordResetDB.token_hash == identificador
            )
            .with_for_update()
        )

        if (
            recuperacion is None
            or recuperacion.used_at is not None
            or (
                fecha_utc(recuperacion.expires_at)
                <= ahora()
            )
        ):
            raise HTTPException(
                status_code=400,
                detail="Token de recuperacion invalido o caducado"
            )

        usuario = db.get(
            UserDB,
            recuperacion.user_id
        )

        if usuario is None:
            raise HTTPException(
                status_code=400,
                detail="Token de recuperacion invalido"
            )

        # Cifrar la nueva contrasena con Argon2
        usuario.password_hash = cifrar_password(
            solicitud.new_password
        )

        # Invalidar los JWT emitidos anteriormente
        invalidacion = db.get(
            UserTokenInvalidationDB,
            usuario.id
        )

        if invalidacion is None:
            db.add(
                UserTokenInvalidationDB(
                    user_id=usuario.id,
                    invalid_before=ahora()
                )
            )
        else:
            invalidacion.invalid_before = ahora()

        # Invalidar todos los enlaces pendientes del usuario
        recuperaciones = db.scalars(
            select(PasswordResetDB).where(
                PasswordResetDB.user_id == usuario.id,
                PasswordResetDB.used_at.is_(None)
            )
        ).all()

        for registro in recuperaciones:
            registro.used_at = ahora()

        db.commit()

    return {
        "message": "Contrasena actualizada correctamente"
    }
