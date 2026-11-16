
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


class AutenticacinApiImpl(BaseAutenticacinApi):

    # POST /auth/register
    # Registrar un nuevo usuario
    async def register_user(
        self,
        register_request: RegisterRequest
    ) -> UserProfile:

        email = str(register_request.email).strip().lower()
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
                detail="La contrasena debe tener al menos 8 caracteres"
            )

        with SessionLocal() as db:

            # Comprobar si el correo ya esta registrado
            usuario_existente = db.scalar(
                select(UserDB).where(
                    UserDB.email == email
                )
            )

            if usuario_existente is not None:
                raise HTTPException(
                    status_code=400,
                    detail="El correo electronico ya esta registrado"
                )

            # Crear el usuario con rol client
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
                    detail="El correo electronico ya esta registrado"
                )

            return UserProfile(
                id=nuevo_usuario.id,
                name=nuevo_usuario.name,
                email=nuevo_usuario.email,
                role=nuevo_usuario.role,
                phone=nuevo_usuario.phone,
                avatar_url=nuevo_usuario.avatar_url
            )

    # POST /auth/login
    # Autenticar al usuario y generar un JWT
    async def login_user(
        self,
        login_request: LoginRequest
    ) -> AuthResponse:

        email = str(login_request.email).strip().lower()
        password = login_request.password

        if isinstance(password, SecretStr):
            password = password.get_secret_value()

        with SessionLocal() as db:

            # Buscar al usuario por correo
            usuario = db.scalar(
                select(UserDB).where(
                    UserDB.email == email
                )
            )

            # No revelar si el correo existe o no
            if usuario is None:
                raise HTTPException(
                    status_code=401,
                    detail="Correo o contrasena incorrectos"
                )

            # Comprobar el hash Argon2
            if not verificar_password(
                password,
                usuario.password_hash
            ):
                raise HTTPException(
                    status_code=401,
                    detail="Correo o contrasena incorrectos"
                )

            # Generar token firmado con el ID y rol
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

    # POST /auth/logout
    # Revocar el JWT utilizado para cerrar la sesion
    async def logout_user(
        self,
        token: str
    ) -> None:

        cerrar_sesion(token)

        return None

    # POST /auth/reset-password
    # Solicitar un enlace para recuperar la contrasena
    async def request_password_reset(
        self,
        request_password_reset_request: RequestPasswordResetRequest
    ) -> None:

        email = str(
            request_password_reset_request.email
        ).strip().lower()

        solicitar_recuperacion(email)

        return None
