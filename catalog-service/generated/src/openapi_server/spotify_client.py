
import os

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


async def obtener_token_spotify() -> str:
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=503,
            detail="Spotify no esta configurado"
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            respuesta = await client.post(
                "https://accounts.spotify.com/api/token",
                data={"grant_type": "client_credentials"},
                auth=(client_id, client_secret)
            )
            respuesta.raise_for_status()
            datos = respuesta.json()

    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(
            status_code=503,
            detail="No se pudo autenticar con Spotify"
        ) from exc

    token = datos.get("access_token")

    if not isinstance(token, str) or not token:
        raise HTTPException(
            status_code=503,
            detail="Spotify no devolvio un token valido"
        )

    return token


async def obtener_cancion_spotify(spotify_id: str) -> dict:
    """
    Consulta los metadatos de una cancion en Spotify.
    """
    token = await obtener_token_spotify()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            respuesta = await client.get(
                f"https://api.spotify.com/v1/tracks/{spotify_id}",
                headers={
                    "Authorization": f"Bearer {token}"
                },
                params={"market": "ES"}
            )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="No se pudo conectar con Spotify"
        ) from exc

    if respuesta.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="Cancion no encontrada en Spotify"
        )

    if respuesta.status_code != 200:
        raise HTTPException(
            status_code=503,
            detail="Spotify no pudo devolver la cancion"
        )

    try:
        datos = respuesta.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=503,
            detail="Respuesta invalida de Spotify"
        ) from exc

    return {
        "spotify_id": datos.get("id"),
        "title": datos.get("name"),
        "spotify_url": (
            datos.get("external_urls", {}).get("spotify")
        ),
        "preview_url": datos.get("preview_url"),
        "artists": [
            artista.get("name")
            for artista in datos.get("artists", [])
        ]
    }
