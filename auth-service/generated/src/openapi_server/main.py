
# coding: utf-8

"""
API de Autenticacion y Cuentas - Subsonic Festival.

Gestiona registro, inicio de sesion, JWT, perfiles
de usuario y recuperacion de contrasenas.
"""

from fastapi import FastAPI
from openapi_server.lifecycle import lifespan

from openapi_server.apis.autenticacin_api import (
    router as AutenticacinApiRouter
)
from openapi_server.apis.usuarios_api import (
    router as UsuariosApiRouter
)
from openapi_server.auth_flows import (
    router as auth_flows_router
)
from openapi_server.login_rate_limit import (
    LoginRateLimitDB  # register the rate-limit table with the shared Base
)


app = FastAPI(
    lifespan=lifespan,
    title="API de Autenticación y Cuentas - Subsonic Festival",
    description=(
        "API responsable de autenticacion, registro, "
        "gestion de sesiones, perfiles de usuario "
        "y asignacion de roles. Proporciona "
        "validacion de identidad a los demas "
        "microservicios de Subsonic Festival."
    ),
    version="1.2.0",
)


app.include_router(auth_flows_router)
app.include_router(AutenticacinApiRouter)
app.include_router(UsuariosApiRouter)

from openapi_server.health import router as health_router
app.include_router(health_router)
