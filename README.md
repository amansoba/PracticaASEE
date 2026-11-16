# Subsonic Festival

Proyecto de ASEE: cinco API FastAPI con PostgreSQL independiente y un frontend
React + TypeScript. Los comandos siguientes parten de esta carpeta `PracticaASEE`,
que contiene el repositorio Git del proyecto y `docker-compose.yml`.

## Arranque reproducible con Docker

Requisitos: Git, Docker con Compose y daemon Linux disponible. La construcción
necesita acceso a los registros de imágenes, PyPI y npm. No hace falta instalar
Python, Node ni PostgreSQL en el host para arrancar el sistema.

Windows (PowerShell):

```powershell
Copy-Item .env.example .env
# Ajustar los valores del archivo .env.
docker compose up --build
```

Linux:

```bash
cp .env.example .env
# Ajustar los valores del archivo .env.
docker compose up --build
```

Para esperar al estado saludable en segundo plano:
`docker compose up --build -d --wait --wait-timeout 180`.
Compose crea las cinco bases, ejecuta los cinco seeds y arranca las API y el
frontend. Las tablas también se inicializan al arrancar cada API. Los volúmenes
persisten al ejecutar `docker compose down`; no es necesario borrar datos para
reconstruir las imágenes.

| Componente | Acceso local | Responsabilidad | Operaciones de negocio |
|---|---|---|---:|
| auth-service | http://localhost:8001/docs | Cuentas, JWT, roles y recuperación de contraseña | 10 |
| event-service | http://localhost:8002/docs | Festivales, line-up, pases, entradas y check-in QR | 12 |
| catalog-service | http://localhost:8003/docs | Artistas, administración de canciones y Spotify opcional | 9 |
| commerce-service | http://localhost:8004/docs | Productos, tallas, stock, pedidos e idempotencia | 12 |
| provider-service | http://localhost:8005/docs | Empresas, administración de servicios/espacios y propuestas | 16 |
| Frontend | http://localhost:5173 | Interfaz React servida por Nginx | — |

Hay **59 operaciones de negocio**, más `GET /health` y `GET /ready` por servicio:
**69 operaciones** en total, contrastadas con FastAPI. Swagger y su documento
`/openapi.json` no se cuentan como operaciones de negocio. La
[matriz de endpoints](docs/endpoints.md) detalla métodos y rutas.

## Configuración y cuentas de demostración

Para Docker se utiliza el `.env` de esta raíz. Para ejecución local, cada API
lee `<servicio>/generated/.env`; las variables del proceso tienen prioridad.
Los valores de ejemplo son exclusivamente de demostración y no deben usarse
como credenciales reales. Los archivos `.env` y `.env.test` están ignorados.

| Variable | Uso |
|---|---|
| `DB_PASSWORD` | Contraseña local de las cinco instancias PostgreSQL de Compose |
| `JWT_SECRET_KEY` | Firma JWT de auth; mínimo 32 caracteres |
| `SEED_PASSWORD` y `SEED_*_EMAIL` | Credenciales demo antes del primer seed |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | Recuperación de contraseña mediante SMTP |
| `PASSWORD_RESET_URL` | URL de la interfaz que recibirá el token de recuperación |
| `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` | Enriquecimiento opcional de canciones |

Compose proporciona `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_NAME`,
`AUTH_SERVICE_URL`, `CATALOG_SERVICE_URL` y `EVENT_SERVICE_URL` según el servicio.
Las bases no publican puertos. No se necesita SMTP ni Spotify para arrancar,
crear datos o ejecutar tests. Sin SMTP configurado, el envío de recuperación
puede devolver 503. La integración incluye la página React de restablecimiento
en `/recuperar-contrasena/confirmar`; `PASSWORD_RESET_URL` apunta a esa ruta.
El envío real por correo requiere configurar SMTP.

| Cuenta | Correo por defecto | Contraseña por defecto |
|---|---|---|
| Administrador | demo.admin@subsonic.example.com | DemoSubsonic2026! |
| Proveedor | demo.provider@subsonic.example.com | DemoSubsonic2026! |
| Cliente | demo.client@subsonic.example.com | DemoSubsonic2026! |

El seed incluye artistas, canciones, géneros como campo del artista, un festival,
line-up, pase, una entrada demo, productos con tallas y stock, empresa, servicio,
espacio y propuesta. Las referencias entre servicios usan identificadores
`demo_*`. No se integra ninguna pasarela de pagos.

El primer arranque ya ejecuta el seed. Para repetirlo:

```bash
docker compose run --rm auth-seed
docker compose run --rm catalog-seed
docker compose run --rm event-seed
docker compose run --rm commerce-seed
docker compose run --rm provider-seed
```

No duplica registros ni sobrescribe contraseñas o stock existentes. Cambiar las
variables demo después del primer seed no modifica las cuentas ya creadas.
Fuera de Docker: `python scripts/seed.py --service auth`, con las dependencias
y el `.env` del servicio configurados; repetir para los otros cuatro servicios.
`python scripts/seed.py` los ejecuta todos con el intérprete actual.

## Pruebas y contratos

Con Compose en ejecución y Python 3.14 en el host:

```bash
python scripts/test_compose.py
```

El script instala dependencias de desarrollo en los contenedores y ejecuta cada
suite en una base `*_test`, además de las pruebas de inicio/seed en otra
`*_seed_test`. No utiliza las bases demo para los tests que borran tablas.
Admite `--service auth` y `--project <nombre>`. No ejecutar suites concurrentes
contra una misma base de pruebas.

El recuento histórico **181/184 corresponde a tests**, no a endpoints. El paquete
de Andrea añadió cinco pruebas del límite de invalidación JWT y cinco de
inicialización/seed. La integración incorpora además las pruebas de rate limiting,
QR, administración, idempotencia y expiración de pedidos. Los resultados actuales
se registran en [validación de la integración](docs/merge-integration.md).

Para validar OpenAPI desde un entorno Python:

```bash
python -m pip install -r scripts/requirements.txt
python scripts/validate_openapi.py
```

Con las dependencias de backend instaladas:
`python scripts/check_runtime_contracts.py` contrasta contratos y FastAPI;
`python scripts/smoke.py` comprueba el despliegue por HTTP y requiere
`python-dotenv`. También puede ejecutarse el smoke desde Docker:

```bash
docker compose exec -T auth python /app/scripts/smoke.py --url http://frontend
```

Las especificaciones raíz son la fuente de verdad. `bash scripts/generate.sh`
(Linux o Git Bash en Windows) genera candidatos en una carpeta temporal;
requiere Docker o Java y el JAR de OpenAPI Generator 7.26.0. No sobrescribe el
código manual de `generated/`. Ver [contratos](docs/openapi.md).

GitHub Actions comprueba backend con PostgreSQL 15, inicio/seed, contratos,
lint y build del frontend, construcción y arranque de Compose y smoke HTTP.
El workflow está preparado; su ejecución en GitHub requiere que los cambios
sean publicados por el equipo. Este trabajo no realiza push.

## Desarrollo sin Docker

Versiones usadas para la validación: **Python 3.14**, **PostgreSQL 15** y
**Node 24**. Las plantillas antiguas de Docker indicaban Python 3.10; no se ha
validado esa versión en este trabajo. Uvicorn, Click y websockets se han
actualizado conjuntamente para permitir el arranque real en Python 3.14.

Crear un entorno virtual por servicio, instalar su `requirements-dev.txt`,
copiar `generated/.env.example` a `generated/.env` y configurar un rol/base
PostgreSQL que ya exista. FastAPI crea las tablas, pero no crea roles ni bases.
Los requisitos completos y ejemplos están en [configuración](docs/setup.md).

Ejemplo para auth desde la raíz:

```powershell
# Windows
py -3.14 -m venv auth-service/generated/.venv
.\auth-service\generated\.venv\Scripts\python -m pip install -r auth-service/generated/requirements-dev.txt
Copy-Item auth-service/generated/.env.example auth-service/generated/.env
# Configurar DB_* y JWT_SECRET_KEY antes de continuar.
.\auth-service\generated\.venv\Scripts\python scripts/seed.py --service auth
.\auth-service\generated\.venv\Scripts\python -m uvicorn openapi_server.main:app --app-dir auth-service/generated/src --host 127.0.0.1 --port 8001
```

```bash
# Linux
python3.14 -m venv auth-service/generated/.venv
auth-service/generated/.venv/bin/python -m pip install -r auth-service/generated/requirements-dev.txt
cp auth-service/generated/.env.example auth-service/generated/.env
# Configurar DB_* y JWT_SECRET_KEY antes de continuar.
auth-service/generated/.venv/bin/python scripts/seed.py --service auth
auth-service/generated/.venv/bin/python -m uvicorn openapi_server.main:app --app-dir auth-service/generated/src --host 127.0.0.1 --port 8001
```

Repetir el procedimiento para catalog, event, commerce y provider con los
puertos de la tabla. Para el frontend: `cd frontend`, `npm ci`, `npm run dev`.
Vite usa los servicios locales de la tabla; Docker utiliza Nginx para esas
mismas rutas `/api/*`. `npm run lint` y `npm run build` ejecutan sus verificaciones.

## Documentación técnica y coordinación

- [Arquitectura y bases de datos](docs/architecture.md).
- [Configuración, tablas y seed](docs/setup.md).
- [Contratos y generación segura](docs/openapi.md).
- [Infraestructura y coordinación con Práctica 3](docs/infrastructure.md).
- [Pruebas](docs/testing.md), [endpoints](docs/endpoints.md) y [verificaciones originales de Andrea](docs/validation.md).
- [Resolución y validación de la integración de Práctica 2](docs/merge-integration.md).
- [Informe de cambios](docs/work-report.md) y [decisiones tecnológicas](PosiblesTecnologías.md).

Se conservan los Dockerfiles y Compose originales de cada servicio; las imágenes
de integración están en `infra/`. El equipo de Práctica 3 deberá revisar su
sustitución cuando están disponibles sus archivos definitivos. No se modifican
archivos del frontend ni se añaden CRUD, pagos u otras funcionalidades de negocio.
