# Verificaciones realizadas

Validación local del paquete de Andrea el 16 de noviembre de 2026, en Windows,
con Docker Desktop Linux. Se utilizaron proyectos y bases de prueba independientes
de cualquier base previa del usuario. No se han publicado cambios en GitHub.

## Resultado final

| Comprobación | Resultado |
|---|---|
| OpenAPI raíz y copias de los cinco servicios | Correctos: sintaxis, semántica, referencias, duplicados y coherencia |
| Contratos frente a FastAPI | 59 operaciones; coinciden rutas, métodos, respuestas declaradas y campos/nulabilidad de esquemas compartidos |
| auth-service | 33 tests superados |
| catalog-service | 27 tests superados |
| event-service | 27 tests superados |
| commerce-service | 56 tests superados |
| provider-service | 46 tests superados |
| Inicialización, seed repetido, salud y acceso a datos | 5 tests superados, uno por servicio |
| Total final de tests | **194 superados**: 189 de servicios y 5 de inicialización |
| Docker Compose | `config --quiet` correcto |
| Construcción de imágenes | Cinco backend y frontend construidos |
| Dependencias instaladas | `pip check` sin conflictos en los cinco contenedores |
| Arranque integrado | Cinco API, cinco PostgreSQL y frontend saludables; cinco seeds con salida 0 |
| HTTP a través de Nginx | SPA, diez sondeos de salud, tres cuentas demo, `/providers/me` y datos de catálogo/eventos/comercio/proveedores correctos |
| Frontend en Node 24 | `npm ci`, `npm run lint` y `npm run build` correctos; fuentes y lockfile sin modificar |
| Generador seguro | Sintaxis Bash comprobada; no se regeneró sobre `generated/` |
| Workflow | YAML revisado y comandos equivalentes ejecutados localmente; sin ejecución hospedada todavía |
| Revisión Git | Sin errores de whitespace, sin `.env`/`.env.test` en el índice ni cambios en archivos del frontend |

La ejecución final de todas las suites utilizó los requisitos reales de cada
imagen, incluido SQLAlchemy 2.1.6/psycopg 3.3.6 en event y 2.0.44/3.2.12 en los
otros servicios. Python del host: 3.14.3; imágenes backend: Python 3.14;
PostgreSQL 15 y Node 24. No se ha probado Python 3.10.

Los recuentos antiguos 181 y 184 eran tests. Los tres tests de `/providers/me`
ya formaban parte de los 184 presentes al empezar; se añaden cinco del límite
temporal JWT y cinco de inicialización/seed. Las operaciones de negocio son 49;
se añaden diez operaciones de salud, no nuevas funciones de negocio.

## Incidencias detectadas y resueltas

1. El entorno inicial no tenía dependencias Python; la creación del venv y el
   acceso al daemon requirieron autorización fuera del sandbox.
2. Cuatro pruebas async de catálogo fallaron inicialmente por ausencia de
   pytest-asyncio. Se declara como dependencia de desarrollo y las suites pasan.
3. Tras una interrupción de herramientas, una repetición de tests se solapó
   con un proceso aún activo y produjo errores de tablas. Se esperó al fin de
   los procesos y se repitieron las pruebas secuencialmente en bases aisladas.
   El runner documentado ejecuta una suite por proceso, sin paralelismo sobre
   una base compartida.
4. Uvicorn 0.13.4 no arrancaba en Python 3.14 por la gestión del bucle de eventos.
   Se actualizó junto con Click. El segundo arranque detectó que websockets 10.0
   era incompatible con el Uvicorn actualizado; se cambió a 15.0.1. El arranque
   final y las pruebas HTTP pasan.

Persiste un aviso de deprecación de Starlette/AnyIO en los tests existentes;
no causa fallos. No se amplían cambios de dependencias para eliminarlo.
SMTP y Spotify reales no se verifican. No se ha ejecutado una regeneración
completa de candidatos: se proporciona el mecanismo seguro y se conserva el
código manual. Las limitaciones de negocio y coordinación están en
[dependencies.md](dependencies.md).

## Repetición de las comprobaciones

```bash
docker compose up --build -d --wait --wait-timeout 180
python scripts/test_compose.py
docker compose exec -T auth python /app/scripts/smoke.py --url http://frontend
python -m pip install -r scripts/requirements.txt
python scripts/validate_openapi.py
```

El nombre de proyecto utilizado para validar localmente fue
`subsonic-andrea-validation`; el PostgreSQL adicional del host para las primeras
pruebas se llamó `subsonic-andrea-test` y publicó únicamente 127.0.0.1:55432.
Los volúmenes se conservan al detener el despliegue de validación.
