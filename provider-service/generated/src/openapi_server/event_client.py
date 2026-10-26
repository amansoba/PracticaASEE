
import os
from pathlib import Path
from urllib.parse import quote

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException


# ============================================================
# CONFIGURACION DEL MICROSERVICIO DE EVENTOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")

EVENT_SERVICE_URL = os.getenv(
    "EVENT_SERVICE_URL",
    "http://127.0.0.1:8002"
).rstrip("/")


# ============================================================
# CONSULTA SINCRONA A EVENTOS
# ============================================================

async def consultar_evento(event_id: str) -> dict:
    """
    Consulta GET /events/{eventId} para comprobar
    que el festival existe.

    Devuelve 404 si el evento no existe y 503
    si el microservicio no responde correctamente.
    """

    if not isinstance(event_id, str) or not event_id.strip():
        raise HTTPException(
            status_code=400,
            detail="El identificador del evento es obligatorio"
        )

    identificador = quote(event_id.strip(), safe="")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            respuesta = await client.get(
                f"{EVENT_SERVICE_URL}/events/{identificador}"
            )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Microservicio de Eventos no disponible"
        ) from exc

    if respuesta.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="El evento indicado no existe"
        )

    if respuesta.status_code != 200:
        raise HTTPException(
            status_code=503,
            detail="No se ha podido consultar el evento"
        )

    try:
        evento = respuesta.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=503,
            detail="Respuesta incorrecta de Eventos"
        ) from exc

    if (
        not isinstance(evento, dict)
        or evento.get("id") != event_id.strip()
    ):
        raise HTTPException(
            status_code=503,
            detail="Datos inconsistentes del evento"
        )

    return evento
