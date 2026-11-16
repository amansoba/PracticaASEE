
from typing import List

from fastapi import HTTPException
from sqlalchemy import select

from openapi_server.apis.usuarios_api_base import BaseUsuariosApi
from openapi_server.models.update_profile_request import (
    UpdateProfileRequest
)
from openapi_server.models.update_user_role_request import (
    UpdateUserRoleRequest
)
from openapi_server.models.user_profile import UserProfile

from openapi_server.database import SessionLocal
from openapi_server.db_models import UserDB


def convertir_perfil(usuario: UserDB) -> UserProfile:
    return UserProfile(
        id=usuario.id,
        name=usuario.name,
        email=usuario.email,
        role=usuario.role,
        phone=usuario.phone,
        avatar_url=usuario.avatar_url
    )


def comprobar_administrador(db, usuario_id: str) -> None:
    usuario = db.get(UserDB, usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Usuario autenticado no encontrado"
        )

    if usuario.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Se requiere rol de administrador"
        )


class UsuariosApiImpl(BaseUsuariosApi):

    # GET /users/me
    async def get_current_user_profile(
        self,
        usuario_id: str
    ) -> UserProfile:

        with SessionLocal() as db:
            usuario = db.get(UserDB, usuario_id)

            if usuario is None:
                raise HTTPException(
                    status_code=404,
                    detail="Usuario no encontrado"
                )

            return convertir_perfil(usuario)

    # PUT /users/me
    async def update_current_user_profile(
        self,
        update_profile_request: UpdateProfileRequest,
        usuario_id: str
    ) -> UserProfile:

        with SessionLocal() as db:
            usuario = db.get(UserDB, usuario_id)

            if usuario is None:
                raise HTTPException(
                    status_code=404,
                    detail="Usuario no encontrado"
                )

            cambios = update_profile_request.model_dump(
                exclude_unset=True
            )

            if "name" in cambios:
                nombre = cambios["name"]

                if not isinstance(nombre, str) or not nombre.strip():
                    raise HTTPException(
                        status_code=400,
                        detail="El nombre no puede estar vacio"
                    )

                usuario.name = nombre.strip()

            if "phone" in cambios:
                usuario.phone = cambios["phone"]

            if "avatar_url" in cambios:
                usuario.avatar_url = cambios["avatar_url"]

            db.commit()
            db.refresh(usuario)

            return convertir_perfil(usuario)

    # GET /users
    async def list_all_users(
        self,
        usuario_id: str
    ) -> List[UserProfile]:

        with SessionLocal() as db:
            comprobar_administrador(db, usuario_id)

            usuarios = db.scalars(
                select(UserDB).order_by(UserDB.name)
            ).all()

            return [
                convertir_perfil(usuario)
                for usuario in usuarios
            ]

    # GET /users/{id}
    async def get_user_by_id(
        self,
        id: str,
        usuario_id: str
    ) -> UserProfile:

        with SessionLocal() as db:
            solicitante = db.get(UserDB, usuario_id)

            if solicitante is None:
                raise HTTPException(
                    status_code=401,
                    detail="Usuario autenticado no encontrado"
                )

            usuario = db.get(UserDB, id)

            if usuario is None:
                raise HTTPException(
                    status_code=404,
                    detail="Usuario no encontrado"
                )

            # Solo el propio usuario o un administrador
            # pueden consultar el perfil completo.
            if (
                solicitante.id != usuario.id
                and solicitante.role != "admin"
            ):
                raise HTTPException(
                    status_code=403,
                    detail="No tienes permiso para consultar este perfil"
                )

            return convertir_perfil(usuario)

    # PUT /users/{id}/role
    async def update_user_role(
        self,
        id: str,
        update_user_role_request: UpdateUserRoleRequest,
        usuario_id: str
    ) -> None:

        with SessionLocal() as db:
            comprobar_administrador(db, usuario_id)

            usuario = db.get(UserDB, id)

            if usuario is None:
                raise HTTPException(
                    status_code=404,
                    detail="Usuario no encontrado"
                )

            nuevo_rol = update_user_role_request.role

            # Admitir tanto str como Enum de Pydantic
            if hasattr(nuevo_rol, "value"):
                nuevo_rol = nuevo_rol.value

            if nuevo_rol not in ("client", "provider", "admin"):
                raise HTTPException(
                    status_code=400,
                    detail="Rol no permitido"
                )

            usuario.role = nuevo_rol

            db.commit()
