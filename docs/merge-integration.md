# Integración de Andrea en Práctica 2

Resolución del merge ya iniciado de `feature/andrea-base-reproducible`
(`8d87072`) sobre `integration/practica2` (`5a032cc`). No se inicia otro merge,
no se aborta el existente y no se modifica `main` (`9938d35`).

## Conflictos y contenido conservado

- El contrato generado de auth ya estaba resuelto manualmente. Se conserva
  su contenido, incluido el 429 del login con cabecera `Retry-After`, eliminando
  únicamente las claves idénticas `summary` y `tags` que estaban repetidas. En el
  contrato raíz se elimina una definición duplicada de confirmación de
  contraseña, conservando el esquema nombrado y todas sus respuestas.
- Se resuelven los otros cuatro contratos generated a partir de la unión
  semántica de las operaciones de ambas ramas. Se contrastan previamente los
  métodos, respuestas, cabeceras, campos y enumeraciones de los dos lados.
  Se conservan administración de canciones, servicios/espacios y pedidos,
  cabecera `Idempotency-Key`, estados, cancelación/pago simulado y check-in QR.
- En `autenticacin_impl.py` el conflicto solo afectaba a comentarios. El AST
  de la implementación resuelta coincide con HEAD: se mantienen rate limiting,
  recuperación y revocación, con un único `logout_user`.
- Los cuatro `main.py` con conflictos conservan todos los routers de HEAD y
  añaden los healthchecks y el lifespan de inicialización. Se comprueba que no
  hay registros duplicados de ruta/método.
- Se corrige también el auto-merge de `auth/main.py`, que duplicaba el argumento
  `lifespan` y ocultaba el import compartido. El modelo `LoginRateLimitDB`
  sigue registrado y `create_all` inicializa también su tabla.
- En commerce se compone el lifespan: primero se crean las tablas, después
  arranca la tarea de expiración; al cerrar se cancela la tarea y se dispone
  el motor. No se cambia la lógica de expiración, pedidos ni idempotencia.
- El seed registra el modelo de intentos de login; la prueba de inicialización
  exige esa tabla y permite que esté vacía, sin sembrar intentos fallidos.
- Los ejemplos y Compose apuntan `PASSWORD_RESET_URL` a la ruta de confirmación
  ya integrada en React: `/recuperar-contrasena/confirmar`.

No se modifican las fuentes de la aplicación ni el lockfile del frontend.
Con autorización expresa del usuario se corrigen únicamente los selectores de
`frontend/e2e/admin-provider.spec.ts`: nombres exactos de campos, mensajes de
estado concretos y espera de opciones adjuntas en un selector habilitado.
Los E2E originales fallaban por ambigüedad de selectores y por exigir visibilidad
a una opción nativa de un selector cerrado; los errores ya estaban en HEAD.
Se conservan los flujos y sus comprobaciones de éxito. El contenido del índice
que no forma parte de estas correcciones se conserva. No se regeneran servidores
ni se incorporan `.env` reales o credenciales.

## Verificación

Los contratos raíz y generated validan sintáctica y semánticamente. Coinciden
con FastAPI: 12 operaciones auth, 11 catalog, 14 event, 14 commerce y 18 provider
(69 en total, incluidas las diez de salud). Python compila y no quedan marcadores
ni archivos sin resolver. La matriz actualizada está en [endpoints.md](endpoints.md).

| Verificación ejecutada | Resultado |
|---|---|
| auth-service | 41 tests superados, incluido rate limiting y recuperación/revocación |
| catalog-service | 33 tests superados, incluida administración de canciones |
| event-service | 33 tests superados, incluido check-in QR |
| commerce-service | 82 tests superados, incluidas idempotencia concurrente, cancelación, pago simulado y expiración automática |
| provider-service | 59 tests superados, incluida administración y adjudicación |
| Inicialización y seed | 5 tests superados, uno por servicio; bases vacías, segunda ejecución y salud |
| Backend e inicialización | **253 tests superados** |
| Frontend Vitest | **19 tests superados** |
| Frontend Playwright/Chromium | **2 E2E superados** tras la corrección autorizada |
| Frontend lint y build | Correctos; lint se repitió sobre los selectores corregidos |
| OpenAPI | Cinco contratos raíz y cinco copias correctos; 69 operaciones coinciden con FastAPI |
| Python | Sintaxis correcta y rutas/métodos registrados una sola vez |
| Docker Compose | Configuración correcta, imágenes construidas, cinco API/cinco PostgreSQL/frontend saludables y cinco seeds con salida 0 |
| Smoke HTTP a través de Nginx | SPA, diez sondeos de salud, tres cuentas demo, perfil proveedor y catálogos correctos |
| Git | Sin marcadores, rutas sin resolver ni errores de whitespace; exclusión de `.env` reales comprobada |

Las pruebas utilizaron el proyecto Docker independiente
`subsonic-merge-validation`, con volúmenes nuevos y bases `*_test` y
`*_seed_test` separadas de la demostración y de los datos existentes del usuario.
Para los E2E se utilizaron las cuentas demo y un espacio libre preparado mediante
las API del propio proyecto aislado, adjudicando previamente propuestas demo
pendientes para evitar interferencias entre escenarios.

Los E2E originales fallaron por campos con etiquetas ambiguas y por esperar
visibilidad en una opción nativa de un selector cerrado. Al probar la corrección
en una copia temporal se detectó además la coexistencia de un mensaje de éxito
y otro de carga con rol `status`. La corrección final, autorizada expresamente,
selecciona el mensaje esperado y conserva todas las acciones y comprobaciones
de éxito. Los dos E2E se volvieron a ejecutar sobre el archivo del repositorio
ya corregido y pasaron.

El workflow conserva las comprobaciones de Andrea y añade `npm test` para incluir
los tests frontend presentes en la integración. Se valida su YAML y se ejecutan
sus comandos localmente; no se ejecuta en GitHub ni se realiza push.

## Límites y observaciones

No se prueban SMTP ni Spotify reales ni una pasarela de pagos real. Persisten
avisos de deprecación de Starlette/AnyIO en los tests existentes. `npm ci`
informa de nueve avisos de vulnerabilidad moderada en las dependencias existentes;
no se ejecuta `npm audit fix` ni se modifica el lockfile fuera del alcance del merge.

No se han aplicado migraciones a bases existentes. `create_all` crea tablas
ausentes y no migra columnas; las verificaciones se realizaron con bases nuevas.
El entorno de validación se detiene al terminar, conservando los volúmenes.
No quedan fallos funcionales pendientes de estas comprobaciones.

## Archivos de resolución

- Los cinco `generated/openapi.yaml` y los cinco contratos raíz: unión de ambas
  ramas, referencias completas y respuestas de validación/conflicto documentadas.
- Los cinco `generated/src/openapi_server/main.py`: routers, lifespan y salud.
- `auth-service/generated/src/openapi_server/impl/autenticacin_impl.py`:
  comentarios del conflicto, sin cambiar el AST de la lógica respecto a HEAD.
- `scripts/seed.py` y `tests/setup_worker.py`: compatibilidad con rate limiting.
- `.env.example`, `auth-service/generated/.env.example` y `docker-compose.yml`:
  URL de recuperación alineada con la pantalla ya implementada.
- `.github/workflows/ci.yml`: ejecución de los tests frontend integrados.
- `frontend/e2e/admin-provider.spec.ts`: únicamente los selectores autorizados.
- `README.md`, `docs/endpoints.md` y este informe: estado actual de la integración.

Los demás archivos preparados por el merge permanecen en el índice sin perder
su contenido. Los informes originales de Andrea se mantienen como registro de
aquella entrega; este documento contiene la verificación de la integración.
