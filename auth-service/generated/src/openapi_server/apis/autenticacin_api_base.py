# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from typing import Any
from typing_extensions import Annotated
from openapi_server.models.auth_response import AuthResponse
from openapi_server.models.login_request import LoginRequest
from openapi_server.models.register_request import RegisterRequest
from openapi_server.models.request_password_reset_request import RequestPasswordResetRequest
from openapi_server.models.user_profile import UserProfile
from openapi_server.security_api import get_token_BearerAuth

class BaseAutenticacinApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseAutenticacinApi.subclasses = BaseAutenticacinApi.subclasses + (cls,)
    async def register_user(
        self,
        register_request: Annotated[RegisterRequest, Field(description="Datos necesarios para el registro del usuario.")],
    ) -> UserProfile:
        """Crea una nueva cuenta de usuario en el sistema con rol predeterminado de cliente. Esta operación es autónoma y no requiere comunicarse con otros microservicios. """
        ...


    async def login_user(
        self,
        login_request: Annotated[LoginRequest, Field(description="Credenciales de acceso del usuario.")],
    ) -> AuthResponse:
        """Autentica las credenciales del usuario y genera un token JWT firmado que contiene su identificador y rol. No requiere comunicación con otros microservicios. """
        ...


    async def logout_user(
        self,
    ) -> None:
        """Invalida la sesión y el token del usuario actual. """
        ...


    async def request_password_reset(
        self,
        request_password_reset_request: Annotated[RequestPasswordResetRequest, Field(description="Dirección de correo del usuario solicitante.")],
    ) -> None:
        """Inicia el flujo de recuperación de contraseña enviando un enlace al correo electrónico proporcionado. """
        ...
