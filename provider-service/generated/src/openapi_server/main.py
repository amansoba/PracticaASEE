
# coding: utf-8

"""
API de Gestion de Proveedores - Subsonic Festival.

Gestion de proveedores, servicios externos, espacios
alquilables, solicitudes y presupuestos.
"""

from fastapi import FastAPI
from openapi_server.lifecycle import lifespan

from openapi_server.apis.presupuestos_y_solicitudes_api import (
    router as PresupuestosYSolicitudesApiRouter
)

from openapi_server.apis.proveedores_api import (
    router as ProveedoresApiRouter
)

from openapi_server.apis.servicios_y_espacios_api import (
    router as ServiciosYEspaciosApiRouter
)

from openapi_server.apis.administracion_servicios_espacios_api import (
    router as AdministracionServiciosEspaciosApiRouter
)


app = FastAPI(
    lifespan=lifespan,
    title="API de Gestion de Proveedores - Subsonic Festival",
    description=(
        "API responsable de la gestion de proveedores, "
        "servicios externos, espacios alquilables, "
        "solicitudes y propuestas de presupuesto."
    ),
    version="1.2.0"
)


app.include_router(PresupuestosYSolicitudesApiRouter)
app.include_router(ProveedoresApiRouter)
app.include_router(ServiciosYEspaciosApiRouter)
app.include_router(AdministracionServiciosEspaciosApiRouter)


from openapi_server.health import router as health_router
app.include_router(health_router)
