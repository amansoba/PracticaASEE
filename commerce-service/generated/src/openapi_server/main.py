
# coding: utf-8

"""
    API de Tienda y Merchandising - Subsonic Festival

    API responsable de la gestion de la tienda oficial,
    productos fisicos, control de stock e inventario por
    tallas y procesamiento de pedidos.

    Se comunica de forma sincronica con Autenticacion
    y Cuentas para validar los usuarios compradores.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from openapi_server.apis.pedidos_api import (
    router as PedidosApiRouter
)
from openapi_server.apis.productos_api import (
    router as ProductosApiRouter
)
from openapi_server.impl.pedidos_impl import (
    expirar_pedidos_pendientes
)


# ============================================================
# CONFIGURACION DE EXPIRACION AUTOMATICA
# ============================================================

logger = logging.getLogger(__name__)

# Revisar los pedidos pendientes cada 60 segundos.
INTERVALO_REVISION_SEGUNDOS = 60


# ============================================================
# TAREA PERIODICA DE EXPIRACION
# ============================================================

async def revisar_pedidos_periodicamente():
    """
    Ejecuta la expiracion de pedidos pendientes
    mientras el microservicio permanezca activo.

    Los errores se registran y no impiden que
    se realicen las siguientes comprobaciones.
    """

    while True:

        try:
            # Ejecutar las operaciones de base de datos
            # en un hilo para no bloquear FastAPI.
            expirados = await asyncio.to_thread(
                expirar_pedidos_pendientes
            )

            if expirados > 0:
                logger.info(
                    "Pedidos caducados y cancelados: %s",
                    expirados
                )

        except Exception:
            logger.exception(
                "Error al revisar pedidos pendientes"
            )

        # Esperar antes de la siguiente comprobacion.
        await asyncio.sleep(
            INTERVALO_REVISION_SEGUNDOS
        )


# ============================================================
# CICLO DE VIDA DE FASTAPI
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Iniciar la tarea de expiracion cuando arranca
    FastAPI y detenerla cuando se cierra.
    """

    tarea_expiracion = asyncio.create_task(
        revisar_pedidos_periodicamente()
    )

    try:
        yield

    finally:
        tarea_expiracion.cancel()

        try:
            await tarea_expiracion
        except asyncio.CancelledError:
            pass


# ============================================================
# APLICACION FASTAPI
# ============================================================

app = FastAPI(
    title="API de Tienda y Merchandising - Subsonic Festival",
    description=(
        "API responsable de la gestion de la tienda "
        "oficial, productos fisicos, control de stock "
        "e inventario por tallas y procesamiento de "
        "pedidos. Para realizar sus operaciones se "
        "comunica de forma sincronica con el "
        "microservicio de Autenticacion y Cuentas."
    ),
    version="1.1.0",
    lifespan=lifespan
)


# ============================================================
# REGISTRO DE ROUTERS
# ============================================================

app.include_router(PedidosApiRouter)
app.include_router(ProductosApiRouter)
