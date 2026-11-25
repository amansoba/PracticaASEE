# Contenedor del microservicio de eventos — Práctica 3

**Autor:** Álvaro
**Microservicio:** `event-service/generated/`
**Commits:** `docker(events): configurar contenedor de eventos` y `docker(compose): integrar despliegue completo de la arquitectura`

## 1. Dockerfile configurado

El Dockerfile definitivo sustituye la plantilla heredada (Python 3.10, sin comando
de arranque) y cumple el contrato de la Práctica 3: puerto interno 8000 y
`GET /ready` para el healthcheck del Compose.

```dockerfile
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/event-service/generated/src

WORKDIR /app/event-service/generated

COPY event-service/generated/requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY event-service/generated/src ./src

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "openapi_server.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Cómo funciona:

- **Base `python:3.14-slim`**: versión validada en la integración (las plantillas
  indicaban Python 3.10, que no está validada en este trabajo).
- **`PYTHONPATH`** apunta a `src` para que el paquete `openapi_server` sea importable.
- Instala únicamente `requirements.txt` y copia solo `src`: imagen mínima de runtime.
- `EXPOSE 8000` y `CMD` arrancan uvicorn en `0.0.0.0:8000`.
- No incluye `seed.py` ni `tests`: el seed y las pruebas corren desde la imagen
  tooling compartida `infra/Dockerfile.backend` (servicio `event-seed`).

## 2. Variables de entorno y conexiones

| Variable | Uso |
|---|---|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Conexión a PostgreSQL `event-db` (base `subsonic_events`) |
| `AUTH_SERVICE_URL` | `http://auth:8000` — valida el JWT contra `GET /users/me` |
| `CATALOG_SERVICE_URL` | `http://catalog:8000` — comprueba el artista con `GET /artists/{id}` antes de asignarlo al line-up |

El servicio se comunica con dos microservicios:

- **Autenticación**: al validar un Bearer token reenvía `GET /users/me` para
  obtener el id y el rol del usuario.
- **Catálogo**: al añadir una actuación al line-up consulta `GET /artists/{id}`
  para verificar que el artista existe.

## 3. Integración en `docker-compose.yml`

- `build`: contexto raíz (`.`) + `dockerfile: event-service/generated/Dockerfile`;
  imagen `subsonic-event:local`.
- Puertos: `127.0.0.1:8002:8000`.
- `depends_on`: `event-seed` completado, `auth` y `catalog` healthy.
- `healthcheck`: `GET /ready` (hace `SELECT 1` sobre PostgreSQL).
- `event-seed` usa la imagen tooling `infra/Dockerfile.backend`.

## 4. Verificación realizada

1. `docker compose config --quiet` → configuración válida.
2. `docker build -f event-service/generated/Dockerfile -t subsonic-event:local .`
   → construye sin errores.
3. Arranque con `event-db` (PostgreSQL 15):
   - `GET /health` → `200`.
   - `GET /ready` → `{"status":"ready"}` (conexión a PostgreSQL correcta).
   - Tablas creadas en `subsonic_events`: `events`, `schedule_entries`,
     `pass_configs`, `tickets`.

## 5. Evidencia a adjuntar en la memoria

- Captura del build del Dockerfile finalizado.
- Captura de las respuestas de `curl /health` y `curl /ready`.
- Captura de `psql -U subsonic -d subsonic_events -c "\dt"` mostrando las cuatro tablas.
