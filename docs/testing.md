# Pruebas

## Ejecución con Docker

Desde la raíz, con Python disponible en el host:

```bash
docker compose up --build -d --wait --wait-timeout 180
python scripts/test_compose.py
docker compose exec -T auth python /app/scripts/smoke.py --url http://frontend
```

`test_compose.py` usa solo la biblioteca estándar en el host. Instala los
`requirements-dev.txt` dentro de cada contenedor; prepara una base `*_test`
y otra `*_seed_test` por servicio. Las bases de demostración permanecen fuera
de las operaciones de limpieza de los tests. La cuenta PostgreSQL de Compose
puede crear bases y actúa como propietaria de las bases de pruebas.

Cada suite se ejecuta en un proceso independiente porque los cinco paquetes
Python se llaman `openapi_server`. No ejecutar `pytest` con todas las carpetas
de servicios en un mismo proceso ni suites concurrentes contra la misma base.

Para otro nombre de proyecto: `python scripts/test_compose.py --project nombre`.
Para un solo servicio: añadir `--service auth` (también catalog, event, commerce,
provider). Requiere acceso al daemon de Docker y a PyPI para dependencias de tests.
Las modificaciones de dependencias de desarrollo quedan en los contenedores,
no se escriben en los archivos del frontend ni en la imagen original.

## Ejecución local

Crear un entorno virtual por servicio e instalar su `requirements-dev.txt`.
Copiar `generated/.env.test.example` a `generated/.env.test` y ajustar host,
puerto, usuario y contraseña. La cuenta indicada debe disponer de su base:

| Servicio | Nombre obligatorio en los tests existentes |
|---|---|
| auth | subsonic_auth_test |
| catalog | subsonic_catalog_test |
| event | subsonic_events_test |
| commerce | subsonic_commerce_test |
| provider | subsonic_providers_test |

Los tests existentes verifican estos nombres y algunos borran/recrean tablas.
No usar bases con datos que se quieran conservar. Ejemplo desde la raíz:

```powershell
.\auth-service\generated\.venv\Scripts\python -m pytest auth-service/generated/tests -q -p no:cacheprovider
```

```bash
auth-service/generated/.venv/bin/python -m pytest auth-service/generated/tests -q -p no:cacheprovider
```

Para las pruebas de inicialización fuera de Docker, preparar también las cinco
bases con los mismos prefijos y sufijo `_seed_test`. Configurar `DB_HOST`,
`DB_PORT`, `DB_USER`, `DB_PASSWORD`, y `JWT_SECRET_KEY` de pruebas en el entorno;
ejecutar `python -m pytest tests/test_setup.py -q -p no:cacheprovider` con las
dependencias backend disponibles. CI crea estas bases automáticamente.

Estas cinco pruebas comprueban creación de tablas durante el lifespan, registro
de las cuatro tablas de auth, dos ejecuciones del seed con recuentos idénticos,
login de administrador o consulta pública de datos, liveness/readiness y una
caída simulada de PostgreSQL que debe devolver 503 sin afectar a `/health`.

## Contratos y frontend

```bash
python -m pip install -r scripts/requirements.txt
python scripts/validate_openapi.py
```

Con dependencias backend: `python scripts/check_runtime_contracts.py`.
No necesita conectarse a PostgreSQL ni a servicios externos.

Con Node 24, desde `frontend`: `npm ci`, `npm run lint`, `npm run build`.
El lockfile se conserva. La validación realizada utilizó Node dentro de Docker,
porque el host Windows no tenía Node instalado.

No se prueba el envío real de correos ni la API real de Spotify: se utilizan
los dobles y configuración de prueba ya disponibles. La CI no necesita secretos
de estas integraciones.
