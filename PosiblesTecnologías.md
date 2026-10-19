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
