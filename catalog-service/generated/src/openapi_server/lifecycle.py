from contextlib import asynccontextmanager

from openapi_server.database import engine
from openapi_server.db_models import Base


@asynccontextmanager
async def lifespan(app):
    # All models have been imported by the routers before startup.
    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        engine.dispose()
