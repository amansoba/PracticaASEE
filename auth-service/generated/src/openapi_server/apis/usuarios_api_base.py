# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from typing import Any, List
from typing_extensions import Annotated
from openapi_server.models.update_profile_request import UpdateProfileRequest
from openapi_server.models.update_user_role_request import UpdateUserRoleRequest
from openapi_server.models.user_profile import UserProfile
from openapi_server.security_api import get_token_BearerAuth

class BaseUsuariosApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseUsuariosApi.subclasses = BaseUsuariosApi.subclasses + (cls,)
    async def get_current_user_profile(
        self,
    ) -> UserProfile:
        """Devuelve la información de perfil asociada al token JWT actual. """
        ...


    async def update_current_user_profile(
        self,
        update_profile_request: Annotated[UpdateProfileRequest, Field(description="Campos de perfil a actualizar.")],
    ) -> UserProfile:
        """Modifica los datos personales básicos del usuario autenticado. """
        ...


    async def list_all_users(
        self,
    ) -> List[UserProfile]:
        """Operación exclusiva para administradores. Lista todos los usuarios registrados en el sistema. """
        ...


    async def get_user_by_id(
        self,
        id: Annotated[str, Field(description="Identificador único del usuario a consultar.")],
    ) -> UserProfile:
        """Devuelve el perfil y estado de un usuario por su ID. Endpoint consultado internamente por Tienda, Gestión de Eventos y Proveedores para verificar existencia y permisos. """
        ...


    async def update_user_role(
        self,
        id: Annotated[str, Field(description="Identificador del usuario cuyo rol será actualizado.")],
        update_user_role_request: Annotated[UpdateUserRoleRequest, Field(description="Nuevo rol a asignar.")],
    ) -> None:
        """Operación exclusiva para administradores. Permite conceder privilegios de proveedor o administrador. """
        ...
