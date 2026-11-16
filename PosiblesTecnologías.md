# Tecnologías: implementación y propuestas iniciales

## Implementación comprobada

| Componente | Tecnología actual | Observaciones |
|---|---|---|
| Cinco microservicios | Python 3.14, FastAPI, Pydantic, Uvicorn | API REST; contratos OpenAPI raíz |
| Persistencia | PostgreSQL 15, SQLAlchemy, psycopg | Base independiente por servicio; create_all al inicio |
| Seguridad | JWT HS256, pwdlib con Argon2 | Propiedad de auth; consultas HTTP desde otras API |
| Frontend | React, TypeScript, Vite, React Router | Node 24 para lint/build; Nginx en Compose |
| Comunicación interna | HTTP REST con httpx | Consultas síncronas, sin mensajería implementada |
| Integraciones opcionales | Spotify y SMTP | No son requisitos para seed ni CI |
| Contratos | OpenAPI 3.0.3, OpenAPI Generator 7.26.0 | Generación temporal sin sobrescribir código manual |
| Desarrollo e integración | Docker Compose, pytest, pytest-asyncio, ESLint | Imágenes independientes en infra/; frontend sin cambios |
| Automatización | GitHub Actions | Workflow preparado y comandos validados localmente; sin publicación |

Las plantillas antiguas usaban Python 3.10. Se valida Python 3.14; se actualizan
Uvicorn, Click y websockets tras comprobar errores de arranque. Los detalles de
versiones y sus diferencias por servicio están en [docs/dependencies.md](docs/dependencies.md).

## Propuestas iniciales conservadas

La tabla siguiente registra el diseño inicial. NestJS, RabbitMQ, un API Gateway
de negocio y un despliegue automatizado publicado no forman parte de la
implementación comprobada. Se conserva esta información como contexto histórico.

Tecnologías propuestas por componente

| Componente | Tecnología recomendada | Motivo |
|---|---|---|
| Autenticación y cuentas | TypeScript + NestJS + PostgreSQL | Validación, seguridad, roles, sesiones y JWT |
| Catálogo musical | TypeScript + NestJS + PostgreSQL | CRUD, consultas de lectura y relaciones artista-canción |
| Gestión de eventos | TypeScript + NestJS + PostgreSQL | Transacciones entre pases, aforo, entradas y eventos |
| Tienda | TypeScript + NestJS + PostgreSQL | Stock, pedidos, estados e idempotencia |
| Proveedores | TypeScript + NestJS + PostgreSQL | Presupuestos, solicitudes y relaciones con eventos |
| Frontend | React + TypeScript | Consistencia de tipos y consumo de APIs OpenAPI |
| Comunicación pública | API Gateway + REST | Punto único de acceso para el frontend |
| Comunicación interna | REST inicialmente; RabbitMQ para eventos | Separar consultas síncronas de procesos asíncronos |
| Desarrollo local | Docker Compose | Levantar todo el sistema de forma reproducible |
| CI/CD | GitHub Actions | Tests, validación OpenAPI, construcción de imágenes y despliegue |
