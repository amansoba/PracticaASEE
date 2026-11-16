# Contratos

La fuente de verdad es `<servicio>/openapi.yaml`. Su copia en `generated/`
es idéntica y se conserva para las herramientas existentes. El servidor
contiene código manual dentro de `generated/`; no se debe regenerar encima.

Validación (desde la raíz): `python -m pip install -r scripts/requirements.txt`
y `python scripts/validate_openapi.py`. Comprueba sintaxis, semántica OpenAPI,
referencias, claves YAML duplicadas, operationId y coherencia de las copias.

Con las dependencias backend instaladas, `python scripts/check_runtime_contracts.py`
contrasta rutas y métodos con FastAPI, respuestas declaradas, campos obligatorios
y nulabilidad de esquemas compartidos. Cada servicio se importa en un intérprete
separado; no abre conexiones a PostgreSQL. Los errores que una implementación
lanza dinámicamente pueden no aparecer en el OpenAPI automático de FastAPI,
por lo que se conservan además las respuestas de negocio documentadas.

Las URL `servers` corresponden al Compose local; no se presupone un despliegue
real en el dominio de ejemplo usado en las propuestas originales.

Generación: `bash scripts/generate.sh` en Linux o Git Bash en Windows.
Requiere Docker o Java con `OPENAPI_GENERATOR_JAR` apuntando al generador
7.26.0 (versión registrada por el proyecto). Produce candidatos en un
directorio temporal, que imprime al comenzar y conserva para revisión.
Integrar manualmente modelos y routers necesarios; no copiar sobre `impl/`,
seguridad, clientes HTTP, persistencia ni tests.
