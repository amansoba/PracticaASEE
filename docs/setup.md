# Configuración e inicialización

Cada servicio usa su PostgreSQL, con `DB_HOST`, `DB_PORT`, `DB_NAME`,
`DB_USER`, `DB_PASSWORD` en `<servicio>/generated/.env` o el entorno.
Las variables del entorno tienen prioridad. Copiar `.env.example` a `.env`
y ajustar los valores; nunca confirmar credenciales.

El lifespan de FastAPI registra todos los modelos y ejecuta
`Base.metadata.create_all(engine)`. Es idempotente; crea tablas nuevas,
no migra tablas ya existentes. No se añade un segundo sistema de migraciones.
Se usa un solo worker durante el arranque inicial para evitar carreras de DDL.

Seed desde la raíz: `python scripts/seed.py`, o `python scripts/seed.py --service auth`.
Cada proceso lee el `.env` del servicio y comparte referencias externas estables
`demo_*`. Ejecutar los cinco en orden auth, catalog, event, commerce, provider.
El seed también crea tablas y se ejecuta en una transacción por servicio.
Una segunda ejecución conserva filas, contraseñas y stock existentes.
No ejecutar semillas concurrentes sobre la misma base de datos.

Cuentas: `demo.admin@subsonic.example.com`, `demo.provider@subsonic.example.com`,
`demo.client@subsonic.example.com`; contraseña de ejemplo `DemoSubsonic2026!`.
Configurar `SEED_PASSWORD`, `SEED_ADMIN_EMAIL`, `SEED_PROVIDER_EMAIL`,
`SEED_CLIENT_EMAIL` antes del primer seed si se necesitan otros valores.
Un cambio posterior de estas variables no modifica cuentas ya creadas.

Se incluyen artistas con género, canciones sin dependencia de Spotify, festival,
line-up, pase con una entrada emitida, productos con tallas y stock, empresa,
servicio, espacio y propuesta. Los géneros son un campo del artista, no una tabla.
Los servicios externos no tienen relación local con las empresas; no se inventa.
Las entradas y referencias entre servicios se insertan directamente sin activar
pagos ni añadir flujos de negocio.

SMTP y Spotify son opcionales para el arranque y el seed; sin credenciales reales
no se verifica envío de correo ni enriquecimiento musical externo.
