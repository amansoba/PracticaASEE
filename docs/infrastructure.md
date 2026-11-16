# Infraestructura y coordinación

Se inspeccionaron las ramas locales y referencias remotas disponibles (main,
feature/auth, catalog, catalog-oscar, commerce-oscar, events, providers-oscar,
integration/oscar). No había una rama identificada como Práctica 3.
Los cinco Dockerfiles actuales son plantillas equivalentes con Python 3.10,
tests durante la construcción y sin comando de arranque; sus Compose solo
levantan un servicio sin PostgreSQL. No sirven para el arranque integrado.
Se conservan intactos y no se fusionan ramas.

`infra/Dockerfile.backend` y `infra/Dockerfile.frontend` son imágenes de
integración independientes. El equipo de Práctica 3 deberá revisar y sustituir
los campos `build` del Compose cuando entregue sus imágenes definitivas,
manteniendo el contrato de configuración y el puerto interno 8000.
No se modifican fuentes ni configuración del frontend. Nginx ofrece las mismas
rutas `/api/*` que el proxy Vite y sirve la SPA construida.

Desde la raíz, copiar `.env.example` a `.env` y ejecutar
`docker compose up --build`. Frontend en http://localhost:5173;
Swagger en http://localhost:8001/docs (auth), 8002 (event), 8003 (catalog),
8004 (commerce), 8005 (provider).

Cinco PostgreSQL 15 con volúmenes independientes, sin puertos publicados.
Cada seed espera su PostgreSQL y cada API espera su seed terminado. Las API
que consultan otras API esperan que respondan a readiness al arrancar.
El orden de arranque no garantiza disponibilidad futura de servicios externos.
`/health` comprueba el proceso; `/ready` hace `SELECT 1` sobre su base local.
Las dependencias HTTP y SMTP/Spotify se validan al ejecutar cada operación.

Repetir seed: `docker compose run --rm auth-seed` y análogamente
`catalog-seed`, `event-seed`, `commerce-seed`, `provider-seed`.
Parar conservando datos: `docker compose down`. No borrar volúmenes para
actualizar el código. Los valores por defecto son exclusivamente demostrativos.

CI instala dependencias y prueba cada servicio por separado con PostgreSQL
aislado; comprueba inicio y seed, valida OpenAPI, ejecuta lint/build del frontend
y construye las imágenes. Python 3.14 corresponde al intérprete local comprobado;
las plantillas antiguas indicaban 3.10. Node 24 se usa para Vite 8/ESLint 10,
según los requisitos registrados en package-lock.json. CI no requiere SMTP ni Spotify.

La primera prueba real detectó que Uvicorn 0.13.4 fallaba en Python 3.14
al obtener el bucle de eventos. Se actualiza a 0.54.0 junto con Click 8.5.1
en los cinco requisitos antes de considerar válido el despliegue. La versión
heredada de websockets 10.0 tampoco es compatible con ese Uvicorn;
se actualiza conjuntamente a 15.0.1, sin añadir rutas WebSocket.
`python scripts/smoke.py` verifica SPA, proxy, salud, cuentas y datos demo
desde el host después del arranque. No imprime JWT ni contraseñas.

`python scripts/test_compose.py` instala dependencias de desarrollo en los
contenedores en ejecución y ejecuta las cinco suites secuencialmente en bases
`*_test` independientes de las bases demo. Admite `--project` y `--service`.
No ejecutar dos suites simultáneamente contra una misma base de pruebas.
