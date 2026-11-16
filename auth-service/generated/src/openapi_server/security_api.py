
from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from openapi_server.models.extra_models import TokenModel
from openapi_server.auth_security import verificar_token
from openapi_server.database import SessionLocal
from openapi_server.db_models import UserDB
from openapi_server.auth_flows import (
    token_revocado,
    token_usuario_invalidado
)

bearer_auth = HTTPBearer(auto_error=False)


def get_token_BearerAuth(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_auth
    )
) -> TokenModel:

    # Comprobar que se ha enviado un token Bearer
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="Token de autenticacion obligatorio",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Verificar la firma y caducidad del JWT
    payload = verificar_token(credentials.credentials)

    if token_revocado(credentials.credentials):
        raise HTTPException(
            status_code=401,
            detail="La sesion ha sido cerrada",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if token_usuario_invalidado(payload):
        raise HTTPException(
            status_code=401,
            detail="La sesion ha sido invalidada",
            headers={"WWW-Authenticate": "Bearer"}
        )

    usuario_id = payload["sub"]

    # Comprobar que el usuario existe en PostgreSQL
    with SessionLocal() as db:

        usuario = db.get(UserDB, usuario_id)

        if usuario is None:
            raise HTTPException(
                status_code=401,
                detail="El usuario del token no existe",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # No confiar en un rol antiguo si ha cambiado
        # desde que se emitio el token.
        if usuario.role != payload["role"]:
            raise HTTPException(
                status_code=401,
                detail="El rol del usuario ha cambiado",
                headers={"WWW-Authenticate": "Bearer"}
            )

    return TokenModel(sub=usuario_id)
