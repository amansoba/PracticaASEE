
# coding: utf-8

"""
API de Catalogo Musical - Subsonic Festival.

Gestion de artistas, canciones y metadatos
musicales con integracion de Spotify.
"""

from fastapi import FastAPI

from openapi_server.apis.artistas_api import (
    router as ArtistasApiRouter
)

from openapi_server.apis.canciones_api import (
    router as CancionesApiRouter
)

from openapi_server.apis.administracion_canciones_api import (
    router as AdministracionCancionesApiRouter
)


app = FastAPI(
    title="API de Catalogo Musical - Subsonic Festival",
    description=(
        "API para la gestion de artistas, canciones, "
        "biografias, generos y metadatos musicales."
    ),
    version="1.2.0"
)


app.include_router(ArtistasApiRouter)
app.include_router(CancionesApiRouter)
app.include_router(AdministracionCancionesApiRouter)
