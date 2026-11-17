# Informe del paquete de Andrea

Trabajo en el repositorio `PracticaASEE`. La rama final es
`feature/andrea-base-reproducible`, creada por indicación posterior del usuario
desde `feature/base-reproducible`. Se conservan los dos primeros commits y la
rama anterior. `main` permanece en `9938d35`. No se realizan push, merges ni PR.

## Bloques entregados

| Bloque | Commit | Resultado |
|---|---|---|
| Contratos y generación | `91000ce` — `fix(openapi): align API contracts and generation` | Esquema de confirmación, proveedor propio, cinco copias sincronizadas, validador y generación temporal segura |
| Persistencia y seed | `82b3d5d` — `feat(setup): initialize databases and seed data` | Tablas al inicio, seed repetible, ejemplos de entorno y pruebas desde bases vacías |
| Infraestructura y CI | `dcdcfec` — `feat(infra): add reproducible deployment and CI` | Compose, cinco PostgreSQL, frontend, seed, salud, contratos refinados y correcciones de compatibilidad del servidor |
| Documentación y limpieza | `docs(chore): finalize documentation and cleanup` | README, tecnologías, arquitectura, matriz, resultados, limpieza de duplicados y cinco pruebas del límite JWT; identificador en `git log -1 --oneline` |

La ruta de recuperación que el usuario había añadido manualmente a
`auth-service/openapi.yaml` se conserva y completa; no se duplica. Las fuentes
del frontend y los Dockerfiles/Compose originales de los servicios se conservan
sin cambios. Las imágenes nuevas están aisladas en `infra/`.

## Funcionalidad del paquete

La clonación puede arrancar mediante Compose sin crear tablas o insertar datos
a mano. El seed permite identificar cuentas y datos de demostración y repetir
su ejecución sin duplicados. Las API ofrecen liveness y readiness de la base.
Los contratos raíz y sus copias validan y coinciden con las rutas implementadas.
El script de generación conserva todo el código manual.

El runner de pruebas instala requisitos de desarrollo en los contenedores y
crea bases `*_test`/`*_seed_test` independientes. Se añaden pruebas del límite
de invalidación, manteniendo la comparación `<=`. La documentación explica
las versiones y los mecanismos reales, incluida la ausencia de una pasarela
de pagos y de una página React para restablecer contraseña.

## Ejecución y resultados

Desde la raíz, copiar `.env.example` a `.env` (PowerShell: `Copy-Item`; Linux:
`cp`), ajustar los valores y ejecutar:

```bash
docker compose up --build
```

Frontend en http://localhost:5173; Swagger en los puertos 8001 (auth), 8002
(event), 8003 (catalog), 8004 (commerce) y 8005 (provider), ruta `/docs`.
El seed se ejecuta automáticamente al arrancar. Para repetirlo:

```bash
docker compose run --rm auth-seed
docker compose run --rm catalog-seed
docker compose run --rm event-seed
docker compose run --rm commerce-seed
docker compose run --rm provider-seed
```

Fuera de Docker: `python scripts/seed.py --service auth` y análogamente para
los otros servicios, con su entorno configurado y sus dependencias instaladas.

Con Compose en marcha:

```bash
python scripts/test_compose.py
docker compose exec -T auth python /app/scripts/smoke.py --url http://frontend
python -m pip install -r scripts/requirements.txt
python scripts/validate_openapi.py
```

Resultado: **194 tests superados** (33 auth, 27 catalog, 27 event, 56 commerce,
46 provider y cinco de inicialización/seed). También pasan lint/build del
frontend, construcción/arranque integrado, smoke HTTP, validación de contratos
y revisión de whitespace. Los comandos de CI se han comprobado localmente;
no se ha ejecutado el workflow en GitHub. Detalle de incidencias iniciales y
verificaciones en [validation.md](validation.md).

## Dependencias y límites

Julia mantiene los pagos y la lógica de negocio pendientes; no bloquean los
datos de demostración preparados. Álvaro deberá integrar la interfaz de
recuperación y sus otras pantallas pendientes. Borja conserva sus módulos de
tienda/proveedores y sus ampliaciones de interfaz. El equipo de Práctica 3
deberá revisar la sustitución futura de las imágenes de integración.
No se han modificado archivos de otros compañeros para resolver esas tareas.

SMTP y Spotify reales quedan sin verificar. No se ha regenerado un servidor
completo, ni validado Python 3.10. `create_all` inicializa pero no migra columnas
existentes. Se preservan las versiones de SQLAlchemy/psycopg distintas de event;
se han probado ambos grupos. Se mantienen avisos de deprecación ajenos a este
paquete. Más contexto en [dependencies.md](dependencies.md).

Los `.env`, credenciales reales, venv, cachés y resultados de compilación no
se incluyen en los commits. El inventario siguiente recoge los cambios frente
al punto inicial `9938d35`, incluyendo el cambio manual conservado del usuario.

## Archivos creados y modificados

| Estado | Archivo |
|---|---|
| A | [.dockerignore](../.dockerignore) |
| A | [.env.example](../.env.example) |
| A | [.gitattributes](../.gitattributes) |
| A | [.github/workflows/ci.yml](../.github/workflows/ci.yml) |
| M | [.gitignore](../.gitignore) |
| M | [PosiblesTecnologías.md](../PosiblesTecnologías.md) |
| M | [README.md](../README.md) |
| M | [auth-service/generated/.env.example](../auth-service/generated/.env.example) |
| A | [auth-service/generated/.env.test.example](../auth-service/generated/.env.test.example) |
| M | [auth-service/generated/openapi.yaml](../auth-service/generated/openapi.yaml) |
| M | [auth-service/generated/requirements-dev.txt](../auth-service/generated/requirements-dev.txt) |
| M | [auth-service/generated/requirements.txt](../auth-service/generated/requirements.txt) |
| M | [auth-service/generated/src/openapi_server/auth_flows.py](../auth-service/generated/src/openapi_server/auth_flows.py) |
| A | [auth-service/generated/src/openapi_server/health.py](../auth-service/generated/src/openapi_server/health.py) |
| M | [auth-service/generated/src/openapi_server/impl/autenticacin_impl.py](../auth-service/generated/src/openapi_server/impl/autenticacin_impl.py) |
| A | [auth-service/generated/src/openapi_server/lifecycle.py](../auth-service/generated/src/openapi_server/lifecycle.py) |
| M | [auth-service/generated/src/openapi_server/main.py](../auth-service/generated/src/openapi_server/main.py) |
| M | [auth-service/generated/src/openapi_server/security_api.py](../auth-service/generated/src/openapi_server/security_api.py) |
| A | [auth-service/generated/tests/test_token_invalidation.py](../auth-service/generated/tests/test_token_invalidation.py) |
| M | [auth-service/openapi.yaml](../auth-service/openapi.yaml) |
| M | [catalog-service/generated/.env.example](../catalog-service/generated/.env.example) |
| A | [catalog-service/generated/.env.test.example](../catalog-service/generated/.env.test.example) |
| M | [catalog-service/generated/openapi.yaml](../catalog-service/generated/openapi.yaml) |
| M | [catalog-service/generated/requirements-dev.txt](../catalog-service/generated/requirements-dev.txt) |
| M | [catalog-service/generated/requirements.txt](../catalog-service/generated/requirements.txt) |
| A | [catalog-service/generated/src/openapi_server/health.py](../catalog-service/generated/src/openapi_server/health.py) |
| A | [catalog-service/generated/src/openapi_server/lifecycle.py](../catalog-service/generated/src/openapi_server/lifecycle.py) |
| M | [catalog-service/generated/src/openapi_server/main.py](../catalog-service/generated/src/openapi_server/main.py) |
| M | [catalog-service/openapi.yaml](../catalog-service/openapi.yaml) |
| A | [commerce-service/generated/.env.test.example](../commerce-service/generated/.env.test.example) |
| M | [commerce-service/generated/openapi.yaml](../commerce-service/generated/openapi.yaml) |
| M | [commerce-service/generated/requirements-dev.txt](../commerce-service/generated/requirements-dev.txt) |
| M | [commerce-service/generated/requirements.txt](../commerce-service/generated/requirements.txt) |
| A | [commerce-service/generated/src/openapi_server/health.py](../commerce-service/generated/src/openapi_server/health.py) |
| A | [commerce-service/generated/src/openapi_server/lifecycle.py](../commerce-service/generated/src/openapi_server/lifecycle.py) |
| M | [commerce-service/generated/src/openapi_server/main.py](../commerce-service/generated/src/openapi_server/main.py) |
| M | [commerce-service/openapi.yaml](../commerce-service/openapi.yaml) |
| A | [docker-compose.yml](../docker-compose.yml) |
| A | [docs/architecture.md](../docs/architecture.md) |
| A | [docs/dependencies.md](../docs/dependencies.md) |
| A | [docs/endpoints.md](../docs/endpoints.md) |
| A | [docs/infrastructure.md](../docs/infrastructure.md) |
| A | [docs/openapi.md](../docs/openapi.md) |
| A | [docs/setup.md](../docs/setup.md) |
| A | [docs/testing.md](../docs/testing.md) |
| A | [docs/validation.md](../docs/validation.md) |
| A | [docs/work-report.md](../docs/work-report.md) |
| M | [event-service/generated/.env.example](../event-service/generated/.env.example) |
| A | [event-service/generated/.env.test.example](../event-service/generated/.env.test.example) |
| M | [event-service/generated/openapi.yaml](../event-service/generated/openapi.yaml) |
| M | [event-service/generated/requirements-dev.txt](../event-service/generated/requirements-dev.txt) |
| M | [event-service/generated/requirements.txt](../event-service/generated/requirements.txt) |
| A | [event-service/generated/src/openapi_server/health.py](../event-service/generated/src/openapi_server/health.py) |
| A | [event-service/generated/src/openapi_server/lifecycle.py](../event-service/generated/src/openapi_server/lifecycle.py) |
| M | [event-service/generated/src/openapi_server/main.py](../event-service/generated/src/openapi_server/main.py) |
| M | [event-service/openapi.yaml](../event-service/openapi.yaml) |
| A | [infra/Dockerfile.backend](../infra/Dockerfile.backend) |
| A | [infra/Dockerfile.frontend](../infra/Dockerfile.frontend) |
| A | [infra/nginx.conf](../infra/nginx.conf) |
| A | [provider-service/generated/.env.test.example](../provider-service/generated/.env.test.example) |
| M | [provider-service/generated/openapi.yaml](../provider-service/generated/openapi.yaml) |
| M | [provider-service/generated/requirements-dev.txt](../provider-service/generated/requirements-dev.txt) |
| M | [provider-service/generated/requirements.txt](../provider-service/generated/requirements.txt) |
| A | [provider-service/generated/src/openapi_server/health.py](../provider-service/generated/src/openapi_server/health.py) |
| A | [provider-service/generated/src/openapi_server/lifecycle.py](../provider-service/generated/src/openapi_server/lifecycle.py) |
| M | [provider-service/generated/src/openapi_server/main.py](../provider-service/generated/src/openapi_server/main.py) |
| M | [provider-service/openapi.yaml](../provider-service/openapi.yaml) |
| A | [pytest.ini](../pytest.ini) |
| A | [scripts/check_runtime_contracts.py](../scripts/check_runtime_contracts.py) |
| A | [scripts/generate.sh](../scripts/generate.sh) |
| A | [scripts/requirements.txt](../scripts/requirements.txt) |
| A | [scripts/seed.py](../scripts/seed.py) |
| A | [scripts/smoke.py](../scripts/smoke.py) |
| A | [scripts/test_compose.py](../scripts/test_compose.py) |
| A | [scripts/validate_openapi.py](../scripts/validate_openapi.py) |
| A | [tests/setup_worker.py](../tests/setup_worker.py) |
| A | [tests/test_setup.py](../tests/test_setup.py) |

A: creado; M: modificado.
