
# coding: utf-8

"""
API de Gestion de Eventos - Subsonic Festival.

Gestiona festivales, line-up, pases, entradas
y validacion de acceso mediante QR.
"""

from fastapi import FastAPI

from openapi_server.apis.eventos_api import (
    router as EventosApiRouter
)
from openapi_server.apis.line_up_api import (
    router as LineUpApiRouter
)
from openapi_server.apis.pases_y_entradas_api import (
    router as PasesYEntradasApiRouter
)
from openapi_server.apis.validacion_entradas_api import (
    router as ValidacionEntradasApiRouter
)


app = FastAPI(
    title="API de Gestion de Eventos - Subsonic Festival",
    description=(
        "API responsable de festivales, programacion, "
        "configuracion de pases, emision de entradas "
        "y validacion de entradas mediante QR."
    ),
    version="1.2.0"
)


app.include_router(EventosApiRouter)
app.include_router(LineUpApiRouter)
app.include_router(PasesYEntradasApiRouter)
app.include_router(ValidacionEntradasApiRouter)
