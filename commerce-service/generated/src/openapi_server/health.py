from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from openapi_server.database import engine

router = APIRouter(tags=["Health"])


@router.get("/health", operation_id="health")
def health():
    """Liveness: the HTTP process responds; no dependency checks."""
    return {"status": "ok"}


@router.get("/ready", operation_id="ready", responses={503: {"description": "Database unavailable"}})
def ready():
    """Readiness: local database is reachable. External APIs are not probed."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database unavailable") from None
    return {"status": "ready"}
