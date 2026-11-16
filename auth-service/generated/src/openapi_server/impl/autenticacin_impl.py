
from uuid import uuid4

from fastapi import HTTPException
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from openapi_server.apis.autenticacin_api_base import (
    BaseAutenticacinApi
)
from openapi_server.models.auth_response import AuthResponse
from openapi_server.models.login_request import LoginRequest
from openapi_server.models.register_request import RegisterRequest
from openapi_server.models.request_password_reset_request import (
    RequestPasswordResetRequest
)
from openapi_server.models.user_profile import UserProfile

from openapi_server.database import SessionLocal
from openapi_server.db_models import UserDB

from openapi_server.auth_security import (
    cifrar_password,
    verificar_password,
    crear_token,
    JWT_EXPIRE_MINUTES
)

from openapi_server.auth_flows import (
    cerrar_sesion,
    solicitar_recuperacion
)

from openapi_server.login_rate_limit import (
    comprobar_limite_login,
    registrar_intento_fallido,
    reiniciar_intentos_login
)


class AutenticacinApiImpl(BaseAutenticacinApi):

    # ========================================================
    # REGISTRO
    # ========================================================

    async def register_user(
        self,
        register_request: RegisterRequest
    ) -> UserProfile:

        email = str(
            register_request.email
        ).strip().lower()

        nombre = register_request.name.strip()
        password = register_request.password

        if isinstance(password, SecretStr):
            password = password.get_secret_value()

        if not nombre:
            raise HTTPException(
                status_code=400,
                detail="El nombre no puede estar vacio"
            )

        if not email:
            raise HTTPException(
                status_code=400,
                detail="El correo electronico es obligatorio"
            )

        if len(password) < 8:
            raise HTTPException(
                status_code=400,
                detail=(
                    "La contrasena debe tener "
                    "al menos 8 caracteres"
                )
            )

        with SessionLocal() as db:

            existente = db.scalar(
                select(UserDB).where(
                    UserDB.email == email
                )
            )

            if existente is not None:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "El correo electronico "
                        "ya esta registrado"
                    )
                )

            nuevo_usuario = UserDB(
                id=f"usr_{uuid4().hex}",
                name=nombre,
                email=email,
                password_hash=cifrar_password(password),
                role="client",
                phone=register_request.phone,
                avatar_url=None
            )

            try:
                db.add(nuevo_usuario)
                db.commit()
                db.refresh(nuevo_usuario)

            except IntegrityError:
                db.rollback()

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "El correo electronico "
                        "ya esta registrado"
                    )
                )

            return UserProfile(
                id=nuevo_usuario.id,
                name=nuevo_usuario.name,
                email=nuevo_usuario.email,
                role=nuevo_usuario.role,
                phone=nuevo_usuario.phone,
                avatar_url=nuevo_usuario.avatar_url
            )

    # ========================================================
    # LOGIN CON LIMITE DE INTENTOS
    # ========================================================

    async def login_user(
        self,
        login_request: LoginRequest
    ) -> AuthResponse:

        email = str(
            login_request.email
        ).strip().lower()

        password = login_request.password

        if isinstance(password, SecretStr):
            password = password.get_secret_value()

        # Comprobar si el usuario esta temporalmente
        # bloqueado por intentos fallidos.
        comprobar_limite_login(email)

        with SessionLocal() as db:

            usuario = db.scalar(
                select(UserDB).where(
                    UserDB.email == email
                )
            )

            # Mensaje identico para usuarios inexistentes
            # y contrasenas incorrectas.
            if (
                usuario is None
                or not verificar_password(
                    password,
                    usuario.password_hash
                )
            ):
                registrar_intento_fallido(email)

                raise HTTPException(
                    status_code=401,
                    detail=(
                        "Correo o contrasena incorrectos"
                    )
                )

            # Un login correcto limpia los fallos.
            reiniciar_intentos_login(email)

            token = crear_token(
                user_id=usuario.id,
                role=usuario.role
            )

            perfil = UserProfile(
                id=usuario.id,
                name=usuario.name,
                email=usuario.email,
                role=usuario.role,
                phone=usuario.phone,
                avatar_url=usuario.avatar_url
            )

            return AuthResponse(
                access_token=token,
                token_type="Bearer",
                expires_in=JWT_EXPIRE_MINUTES * 60,
                user=perfil
            )

    # ========================================================
    # CIERRE DE SESION
    # ========================================================

    # POST /auth/logout
    # Revocar el JWT utilizado para cerrar la sesion
    async def logout_user(
        self,
        token: str
    ) -> None:

        cerrar_sesion(token)
        return None

    # ========================================================
    # RECUPERACION DE CONTRASENA
    # ========================================================

    async def request_password_reset(
        self,
        request_password_reset_request:
        RequestPasswordResetRequest
    ) -> None:

        email = str(
            request_password_reset_request.email
        ).strip().lower()

        solicitar_recuperacion(email)

        return None
