# Dependencias y trabajo pendiente

Se revisaron los cinco `requirements.txt`. Commerce ya coincide con catalog
y provider en sus dependencias de ejecución; no se detectó una divergencia que
justifique cambiar sus versiones de SQLAlchemy o psycopg.

Auth añade `pwdlib[argon2]` y `PyJWT`, necesarios para contraseñas y JWT.
Event utiliza SQLAlchemy 2.1.6 y psycopg 3.3.6; los otros cuatro usan
SQLAlchemy 2.0.44 y psycopg 3.2.12. Se conservan estos límites por servicio.
Ambos grupos se prueban con sus propios requisitos en Docker. No se centralizan
requisitos ni se cambia la arquitectura para imponer una única versión.

Se actualizan conjuntamente Uvicorn 0.54.0, Click 8.5.1 y websockets 15.0.1
por incompatibilidades de arranque comprobadas con Python 3.14. Se añade
pytest-asyncio 1.5.0 porque los tests de seguridad existentes lo necesitan.
Se conservan otras dependencias de las plantillas: su retirada requiere una
revisión separada y no es necesaria para este paquete.

Se elimina el primer `logout_user`, que devolvía 501 y ya estaba sobrescrito por
una segunda definición que sí revoca el token. Se elimina el import duplicado
de `token_revocado`. No cambia el método que Python ejecutaba.

Se conserva `iat <= invalid_before`. JWT codifica `iat` en segundos y el corte
puede tener microsegundos: aceptar la igualdad permitiría conservar tokens de
la misma marca temporal. Las pruebas cubren antes, igualdad, microsegundos,
después y ausencia de invalidación. Un token nuevo emitido en el mismo segundo
del restablecimiento también puede ser rechazado: es la política conservadora
existente, que no se modifica en esta tarea.

## Coordinación

- **Julia:** la pasarela de pagos real está pendiente y la emisión de entradas
  sigue siendo de desarrollo, como indica la implementación existente. No bloquea
  la persistencia inicial ni el seed. No se han añadido CRUD ni lógica de negocio.
- **Álvaro:** falta una ruta/formulario React para completar la recuperación por
  correo; `PASSWORD_RESET_URL` es configurable y el endpoint backend existe.
  Las interfaces administrativas o de entradas que no figuran en `App.tsx`
  siguen fuera de este paquete.
- **Borja:** se conservan los módulos actuales de tienda y proveedores; cualquier
  ampliación de interfaz o administración corresponde a su trabajo. No hay una
  dependencia de esos cambios para ejecutar el seed o los tests del backend.
- **Equipo Práctica 3:** no se dispone de una rama identificada con las imágenes
  definitivas. Se conservan sus plantillas y se documenta la integración en
  `infrastructure.md`. Las nuevas imágenes están separadas en `infra/`.

No se verifican servicios reales de SMTP ni Spotify ni se presupone un despliegue
en el dominio de ejemplo. El workflow se valida localmente y sus comandos se
ejecutan en el entorno disponible; la ejecución hospedada en GitHub queda
pendiente de publicación por el equipo. No se realiza push en esta tarea.
