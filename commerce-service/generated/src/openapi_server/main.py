
# coding: utf-8

import asyncio
import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from openapi_server.lifecycle import lifespan as database_lifespan

from openapi_server.apis.pedidos_api import (
    router as PedidosApiRouter
)
from openapi_server.apis.productos_api import (
    router as ProductosApiRouter
)
from openapi_server.apis.administracion_pedidos_api import (
    router as AdministracionPedidosApiRouter
)
from openapi_server.impl.pedidos_impl import (
    expirar_pedidos_pendientes
)


logger = logging.getLogger(__name__)

INTERVALO_REVISION_SEGUNDOS = 60


# ============================================================
# EXPIRACION AUTOMATICA DE PEDIDOS
# ============================================================

async def revisar_pedidos_periodicamente():

    while True:

        try:
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

        await asyncio.sleep(
            INTERVALO_REVISION_SEGUNDOS
        )


# ============================================================
# CICLO DE VIDA
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    async with database_lifespan(app):
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
# APLICACION
# ============================================================

app = FastAPI(
    lifespan=lifespan,
    title="API de Tienda y Merchandising - Subsonic Festival",
    description=(
        "API responsable de productos, inventario, "
        "pedidos, pagos simulados, cancelaciones "
        "y administracion de compras."
    ),
    version="1.1.0",
)


app.include_router(PedidosApiRouter)
app.include_router(ProductosApiRouter)
app.include_router(AdministracionPedidosApiRouter)


from openapi_server.health import router as health_router
app.include_router(health_router)
