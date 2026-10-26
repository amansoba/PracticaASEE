# Subsonic Festival

## 1. Descripción del proyecto

Subsonic Festival es una plataforma para la gestión de festivales musicales, desarrollada como proyecto de la asignatura ASEE.

El backend utiliza una arquitectura de microservicios. Cada servicio gestiona una parte de la plataforma y dispone de su propia base de datos PostgreSQL.

El sistema contempla autenticación y cuentas, catálogo musical, gestión de eventos, tienda de merchandising y gestión de proveedores.

## 2. Arquitectura del backend

El proyecto está dividido en cinco microservicios independientes:

| Microservicio | Puerto | Responsabilidad |
|---|---|---|
| Autenticación | 8001 | Registro, inicio de sesión, JWT, perfiles y roles |
| Eventos | 8002 | Festivales, programación, pases y entradas |
| Catálogo Musical | 8003 | Artistas, canciones e información musical |
| Tienda | 8004 | Productos, variantes, stock y pedidos |
| Proveedores | 8005 | Empresas proveedoras, servicios, espacios y propuestas |

Cada microservicio expone una API REST mediante FastAPI y dispone de documentación OpenAPI.

## 3. Tecnologías utilizadas

- Python 3.14
- FastAPI y Uvicorn
- PostgreSQL
- SQLAlchemy
- psycopg
- Pydantic
- JWT para autenticación y autorización
- httpx para comunicación HTTP entre microservicios
- pytest para pruebas automatizadas
- Git y GitHub para control de versiones

Las APIs están basadas en contratos OpenAPI y parte de su estructura se ha generado mediante OpenAPI Generator.

## 4. Requisitos previos

Para ejecutar el proyecto localmente se necesita:

- Python y pip
- PostgreSQL
- Git
- Un editor como Visual Studio Code

La integración se ha probado en Windows, utilizando PowerShell, Python 3.14 y PostgreSQL 15.

## 5. Obtener el proyecto

Clonar el repositorio desde GitHub y situarse en su carpeta raíz.

Para trabajar con la versión de integración:

```powershell
git switch integration/oscar
```

## 6. Configuración de PostgreSQL

Cada microservicio utiliza una base de datos independiente.

| Servicio | Base de datos | Usuario |
|---|---|---|
| Autenticación | subsonic_auth | auth_user |
| Eventos | subsonic_events | event_user |
| Catálogo | subsonic_catalog | catalog_user |
| Tienda | subsonic_commerce | commerce_user |
| Proveedores | subsonic_providers | provider_user |

Las bases de datos y los usuarios deben existir en PostgreSQL y disponer de los permisos necesarios.

También existen bases de datos independientes para ejecutar las pruebas:

| Servicio | Base de datos de pruebas |
|---|---|
| Autenticación | subsonic_auth_test |
| Eventos | subsonic_events_test |
| Catálogo | subsonic_catalog_test |
| Tienda | subsonic_commerce_test |
| Proveedores | subsonic_providers_test |

**Importante:** Las pruebas pueden borrar y recrear tablas en las bases de datos terminadas en `_test`. No deben ejecutarse utilizando las bases de datos principales.

## 7. Variables de entorno

Cada microservicio necesita un archivo `.env` dentro de su carpeta `generated`.

Ejemplo de configuración de PostgreSQL:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=NOMBRE_BASE_DATOS
DB_USER=USUARIO_POSTGRESQL
DB_PASSWORD=CONTRASEÑA_LOCAL
```

Se deben sustituir los valores según el microservicio correspondiente.

### Autenticación

Además de la configuración de PostgreSQL, Autenticación necesita:

```dotenv
JWT_SECRET_KEY=CLAVE_SECRETA_DE_AL_MENOS_32_CARACTERES
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

La clave debe generarse de forma segura y mantenerse privada.

### Servicios que consultan Autenticación

Los servicios correspondientes utilizan:

```dotenv
AUTH_SERVICE_URL=http://127.0.0.1:8001
```

### Proveedores

Proveedores también necesita la dirección del microservicio de Eventos:

```dotenv
EVENT_SERVICE_URL=http://127.0.0.1:8002
```

### Configuración de las pruebas

Cada microservicio dispone de un archivo `.env.test` con las credenciales de su base de datos de pruebas.

Su estructura básica es:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=NOMBRE_BASE_DATOS_TEST
DB_USER=USUARIO_POSTGRESQL
DB_PASSWORD=CONTRASEÑA_LOCAL
```

Los archivos `.env` y `.env.test` están excluidos del repositorio mediante `.gitignore`.

**Nunca deben subirse contraseñas, claves JWT ni credenciales reales a GitHub.**

## 8. Instalación de dependencias

Los microservicios tienen entornos virtuales independientes.

Desde la raíz del repositorio, para instalar Autenticación:

```powershell
cd .\auth-service\generated

python -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements-dev.txt
```

El mismo procedimiento debe repetirse en los demás microservicios, sustituyendo la carpeta:

- `event-service/generated`
- `catalog-service/generated`
- `commerce-service/generated`
- `provider-service/generated`

Los archivos `requirements-dev.txt` están destinados a instalar las dependencias necesarias para desarrollo y pruebas, mientras que `requirements.txt` contiene las dependencias de ejecución.

## 9. Arranque de los microservicios

Es necesario abrir cinco terminales independientes.

Todos los comandos siguientes se ejecutan desde la carpeta `generated` del microservicio correspondiente, con su entorno virtual preparado.

### Autenticación — Puerto 8001

```powershell
python -m uvicorn openapi_server.main:app --app-dir src --host 127.0.0.1 --port 8001
```

### Eventos — Puerto 8002

```powershell
python -m uvicorn openapi_server.main:app --app-dir src --host 127.0.0.1 --port 8002
```

### Catálogo Musical — Puerto 8003

```powershell
python -m uvicorn openapi_server.main:app --app-dir src --host 127.0.0.1 --port 8003
```

### Tienda — Puerto 8004

```powershell
python -m uvicorn openapi_server.main:app --app-dir src --host 127.0.0.1 --port 8004
```

### Proveedores — Puerto 8005

```powershell
python -m uvicorn openapi_server.main:app --app-dir src --host 127.0.0.1 --port 8005
```

Se recomienda iniciar primero Autenticación y Eventos, ya que otros servicios necesitan comunicarse con ellos.

## 10. Documentación de las APIs

Cada microservicio ofrece documentación interactiva mediante Swagger UI.

| Servicio | Swagger |
|---|---|
| Autenticación | http://127.0.0.1:8001/docs |
| Eventos | http://127.0.0.1:8002/docs |
| Catálogo | http://127.0.0.1:8003/docs |
| Tienda | http://127.0.0.1:8004/docs |
| Proveedores | http://127.0.0.1:8005/docs |

Los contratos OpenAPI también están disponibles en `/openapi.json`.

## 11. Pruebas automatizadas

Cada microservicio tiene su propia batería de pruebas con pytest.

Para ejecutarlas, situarse en la carpeta `generated` correspondiente y utilizar:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Resultados obtenidos durante la validación de integración del 26 de octubre de 2026:

| Microservicio | Tests superados |
|---|---:|
| Autenticación | 28 |
| Eventos | 27 |
| Catálogo Musical | 27 |
| Tienda | 56 |
| Proveedores | 43 |
| **Total** | **181** |

Todas las pruebas automatizadas finalizaron correctamente en el entorno de integración utilizado.

## 12. Pruebas de integración realizadas

Además de pytest, se realizaron peticiones HTTP reales con los microservicios arrancados simultáneamente.

Se comprobaron los siguientes flujos:

- Registro de usuarios e inicio de sesión.
- Generación de tokens JWT.
- Asignación de roles mediante una cuenta administradora.
- Registro de una empresa con un usuario `provider`.
- Rechazo de peticiones protegidas sin autenticación.
- Comunicación de Proveedores con Autenticación.
- Creación de eventos y consulta de sus datos.
- Publicación de espacios asociados a eventos.
- Envío y recuperación de propuestas de presupuesto.
- Comunicación HTTP de Proveedores con Eventos.
- Creación y consulta de artistas.
- Creación de productos con variantes y existencias.
- Registro y recuperación de pedidos.
- Actualización del stock después de una compra.

Como ejemplo, se comprobó una compra de dos camisetas de talla M con precio unitario de 25 €, obteniendo un pedido de 50 € y una reducción de existencias de 20 a 18 unidades.

Estas comprobaciones validan los flujos mencionados, pero no sustituyen una batería exhaustiva de pruebas de integración, seguridad, rendimiento y despliegue.

## 13. Estado del proyecto

La rama `integration/oscar` reúne los cinco microservicios del backend.

El código de cada servicio se integró desde su respectiva rama de desarrollo y se verificó mediante pruebas automatizadas y peticiones HTTP.

La rama `main` se mantiene separada de los trabajos de integración hasta acordar su incorporación al proyecto principal.

Quedan pendientes de completar y verificar las funcionalidades restantes, la integración del frontend y la preparación del despliegue definitivo.

## 14. Buenas prácticas

- Utilizar una rama independiente para cada funcionalidad.
- Evitar subir archivos `.env`, credenciales y entornos virtuales.
- No ejecutar las pruebas con bases de datos de producción.
- Mantener actualizadas las dependencias de cada microservicio.
- Ejecutar los tests antes de incorporar cambios.
- Coordinar las fusiones de ramas con los integrantes del equipo.
