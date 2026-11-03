
# Subsonic Festival

Plataforma web para la gestión de festivales musicales, desarrollada como proyecto de la asignatura Arquitecturas y Servicios de Entornos Empresariales (ASEE).

El sistema utiliza una arquitectura de microservicios con un backend desarrollado en Python y FastAPI, bases de datos PostgreSQL independientes y un frontend desarrollado con React y TypeScript.

## 1. Descripción del proyecto

Subsonic Festival permite consultar información sobre festivales y artistas, gestionar usuarios con distintos roles, comprar merchandising y administrar empresas proveedoras y propuestas de presupuesto.

El sistema está dividido en cinco microservicios independientes y una aplicación frontend.

Las comunicaciones se realizan mediante APIs REST y peticiones HTTP. Los servicios utilizan contratos OpenAPI y disponen de documentación interactiva mediante Swagger UI.

## 2. Arquitectura del sistema

El proyecto contiene los siguientes componentes:

| Componente | Puerto | Responsabilidad |
|---|---|---|
| Autenticación | 8001 | Registro, login, JWT, usuarios y roles |
| Gestión de Eventos | 8002 | Festivales, eventos, programación y entradas |
| Catálogo Musical | 8003 | Artistas, canciones e información musical |
| Comercio | 8004 | Productos, variantes, existencias y pedidos |
| Proveedores | 8005 | Empresas, servicios, espacios y presupuestos |
| Frontend React | 5173 | Interfaz web para los usuarios |

Cada microservicio dispone de su propia base de datos PostgreSQL y se ejecuta de manera independiente.

El frontend se comunica con ellos mediante un proxy configurado en Vite.

### Estructura del repositorio

```text
PracticaASEE/
├── auth-service/
├── catalog-service/
├── event-service/
├── commerce-service/
├── provider-service/
├── frontend/
├── docs/
├── README.md
├── PosiblesTecnologías.md
└── .gitignore
```

Cada microservicio contiene su contrato `openapi.yaml` y una carpeta `generated` con el servidor FastAPI, la lógica de negocio, los modelos y las pruebas.

## 3. Tecnologías utilizadas

### Backend

- Python 3.14
- FastAPI
- Uvicorn
- PostgreSQL
- SQLAlchemy
- psycopg
- Pydantic
- JWT para autenticación
- httpx para comunicación entre microservicios
- pytest para pruebas automatizadas
- OpenAPI y OpenAPI Generator

### Frontend

- React
- TypeScript
- Vite
- React Router
- CSS
- Fetch API
- ESLint

### Herramientas de desarrollo

- Visual Studio Code
- Git y GitHub
- PowerShell en Windows
- Swagger UI

La integración se ha probado en Windows, utilizando PostgreSQL 15 y Python 3.14.

## 4. Requisitos previos

Para ejecutar el proyecto localmente se necesita:

- Python compatible con las dependencias del backend.
- Node.js y npm.
- PostgreSQL.
- Git.
- Un editor como Visual Studio Code.

Los seis componentes se ejecutan localmente en puertos diferentes.

Es necesario disponer de las bases de datos y de los archivos de configuración correspondientes.

## 5. Obtener el proyecto

El código integrado se encuentra en la rama `main`.

Para clonar el repositorio:

```powershell
git clone https://github.com/amansoba/PracticaASEE.git
cd PracticaASEE
```

Para actualizar una copia existente:

```powershell
git switch main
git pull origin main
```

Antes de realizar cambios, es recomendable comprobar el estado del repositorio:

```powershell
git status -sb
```

En el trabajo en equipo se deben coordinar los cambios antes de modificar archivos compartidos.

## 6. Configuración de PostgreSQL

Cada microservicio utiliza una base de datos independiente.

| Microservicio | Base de datos | Usuario |
|---|---|---|
| Autenticación | subsonic_auth | auth_user |
| Eventos | subsonic_events | event_user |
| Catálogo Musical | subsonic_catalog | catalog_user |
| Comercio | subsonic_commerce | commerce_user |
| Proveedores | subsonic_providers | provider_user |

Las bases de datos y los usuarios deben crearse en PostgreSQL y disponer de los permisos correspondientes.

También se utilizan bases de datos independientes para las pruebas automatizadas:

| Microservicio | Base de datos de pruebas |
|---|---|
| Autenticación | subsonic_auth_test |
| Eventos | subsonic_events_test |
| Catálogo Musical | subsonic_catalog_test |
| Comercio | subsonic_commerce_test |
| Proveedores | subsonic_providers_test |

Las pruebas pueden eliminar y recrear tablas en las bases de datos terminadas en `_test`.

No deben ejecutarse sobre las bases de datos utilizadas para el funcionamiento normal del sistema.

## 7. Variables de entorno

Cada microservicio utiliza un archivo `.env` dentro de su carpeta `generated`.

Los archivos `.env.example` del repositorio sirven como referencia para preparar la configuración local.

### Configuración de PostgreSQL

Ejemplo:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=NOMBRE_BASE_DATOS
DB_USER=USUARIO_POSTGRESQL
DB_PASSWORD=CONTRASENA_LOCAL
```

Los valores deben adaptarse a la base de datos de cada microservicio.

### Autenticación

El servicio de Autenticación necesita también:

```dotenv
JWT_SECRET_KEY=CLAVE_SECRETA_DE_AL_MENOS_32_CARACTERES
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

La clave JWT debe generarse de forma segura y mantenerse privada.

### Comunicación con Autenticación

Los microservicios que consultan la identidad de los usuarios utilizan:

```dotenv
AUTH_SERVICE_URL=http://127.0.0.1:8001
```

### Comunicación con Eventos

Proveedores también utiliza la dirección del microservicio de Eventos:

```dotenv
EVENT_SERVICE_URL=http://127.0.0.1:8002
```

### Configuración de las pruebas

Cada servicio utiliza un archivo `.env.test` con las credenciales de su base de datos de pruebas.

Los archivos `.env` y `.env.test` están excluidos del control de versiones.

Nunca deben subirse contraseñas reales, secretos JWT ni credenciales privadas al repositorio.

## 8. Instalación del backend

Los microservicios tienen entornos virtuales independientes.

Por ejemplo, para preparar Autenticación desde la raíz del proyecto:

```powershell
cd .\auth-service\generated
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

El mismo procedimiento se realiza en las carpetas:

- `event-service/generated`
- `catalog-service/generated`
- `commerce-service/generated`
- `provider-service/generated`

`requirements.txt` contiene las dependencias de ejecución y `requirements-dev.txt` incorpora las necesarias para desarrollo y pruebas.

Los entornos virtuales no se almacenan en GitHub.

## 9. Arranque de los microservicios

Antes de arrancar los servicios debe estar iniciado PostgreSQL.

Cada microservicio necesita una terminal independiente.

Los siguientes comandos parten de la raíz `PracticaASEE`.

### Terminal 1 - Autenticación

```powershell
cd .\auth-service\generated
.\.venv\Scripts\python.exe -m uvicorn openapi_server.main:app --app-dir src --host 127.0.0.1 --port 8001
```

### Terminal 2 - Eventos

```powershell
cd .\event-service\generated
.\.venv\Scripts\python.exe -m uvicorn openapi_server.main:app --app-dir src --host 127.0.0.1 --port 8002
```

### Terminal 3 - Catálogo Musical

```powershell
cd .\catalog-service\generated
.\.venv\Scripts\python.exe -m uvicorn openapi_server.main:app --app-dir src --host 127.0.0.1 --port 8003
```

### Terminal 4 - Comercio

```powershell
cd .\commerce-service\generated
.\.venv\Scripts\python.exe -m uvicorn openapi_server.main:app --app-dir src --host 127.0.0.1 --port 8004
```

### Terminal 5 - Proveedores

```powershell
cd .\provider-service\generated
.\.venv\Scripts\python.exe -m uvicorn openapi_server.main:app --app-dir src --host 127.0.0.1 --port 8005
```

Se recomienda arrancar primero Autenticación y Eventos, ya que otros servicios pueden necesitar comunicarse con ellos.

Para detener cada servidor puede utilizarse `Ctrl + C` en su terminal.

## 10. Instalación y ejecución del frontend

El frontend utiliza React, TypeScript y Vite.

Desde la raíz del repositorio:

```powershell
cd frontend
npm install
```

Para iniciar el servidor de desarrollo:

```powershell
npm run dev
```

La aplicación estará disponible en:

http://localhost:5173

Para utilizar las funcionalidades integradas, los microservicios y PostgreSQL deben estar funcionando.

### Comprobaciones de calidad

Desde la carpeta `frontend`:

```powershell
npm run lint
```

Este comando comprueba el código mediante ESLint.

Para verificar TypeScript y generar la versión de producción:

```powershell
npm run build
```

La compilación genera una carpeta `dist`, que está excluida del repositorio.

## 11. Comunicación entre frontend y backend

El frontend utiliza un proxy configurado en `frontend/vite.config.ts`.

| Ruta frontend | Microservicio | Puerto |
|---|---|---|
| `/api/auth` | Autenticación | 8001 |
| `/api/eventos` | Eventos | 8002 |
| `/api/catalogo` | Catálogo Musical | 8003 |
| `/api/tienda` | Comercio | 8004 |
| `/api/proveedores` | Proveedores | 8005 |

Esta configuración permite realizar las peticiones desde React sin escribir directamente los puertos de los microservicios en cada componente.

La comunicación se realiza mediante peticiones HTTP y respuestas JSON.

Las operaciones protegidas envían el token JWT en la cabecera `Authorization`.

## 12. Funcionalidades implementadas

### Autenticación y usuarios

- Registro de nuevos usuarios.
- Inicio y cierre de sesión.
- Autenticación mediante JWT.
- Roles `client`, `provider` y `admin`.
- Consulta de datos del usuario autenticado.
- Restricciones de acceso según los permisos.

### Eventos

- Consulta de eventos registrados.
- Visualización de festivales disponibles.
- API para crear, modificar y eliminar eventos con los permisos correspondientes.

### Catálogo Musical

- Consulta de artistas.
- Información musical almacenada en PostgreSQL.
- APIs para gestionar los elementos del catálogo.

### Comercio

- Consulta de productos de merchandising.
- Variantes de productos y tallas.
- Consulta de existencias.
- Realización de pedidos autenticados.
- Actualización del stock tras una compra.
- Consulta del historial de pedidos.

### Proveedores

- Registro de empresas proveedoras.
- Gestión de espacios y servicios.
- Propuestas de presupuesto.
- Consulta de propuestas de una empresa.
- Consulta de la propia empresa mediante `GET /providers/me`.
- Listado administrativo de proveedores.

### Frontend React

La interfaz permite:

- Navegar entre las secciones principales.
- Consultar eventos y artistas.
- Registrarse e iniciar sesión.
- Comprar productos de merchandising.
- Consultar pedidos.
- Acceder al panel del proveedor.
- Consultar el listado administrativo de proveedores.

Las funciones disponibles en la interfaz dependen del rol del usuario.

No todas las operaciones administrativas del backend tienen todavía un formulario específico en React.

## 13. Documentación de las APIs

Los cinco microservicios ofrecen Swagger UI.

| Servicio | URL |
|---|---|
| Autenticación | http://127.0.0.1:8001/docs |
| Eventos | http://127.0.0.1:8002/docs |
| Catálogo | http://127.0.0.1:8003/docs |
| Comercio | http://127.0.0.1:8004/docs |
| Proveedores | http://127.0.0.1:8005/docs |

Cada API también expone su contrato a través de `/openapi.json`.

Los archivos `openapi.yaml` del repositorio contienen la definición de los servicios.

## 14. Pruebas automatizadas

Cada microservicio dispone de pruebas automatizadas con pytest.

Para ejecutarlas, debe utilizarse el entorno virtual de cada servicio.

Por ejemplo, desde `auth-service/generated`:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Este procedimiento se repite en los demás microservicios, dentro de sus carpetas `generated`.

Resultados obtenidos durante el desarrollo y las comprobaciones de integración:

| Microservicio | Tests superados |
|---|---:|
| Autenticación | 28 |
| Eventos | 27 |
| Catálogo Musical | 27 |
| Comercio | 56 |
| Proveedores | 46 |
| **Total** | **184** |

Los 181 tests iniciales se ampliaron a 184 después de incorporar tres pruebas para el endpoint `GET /providers/me`.

Estas pruebas comprueban, entre otros aspectos, el acceso de proveedores, el rechazo de clientes sin permisos y el comportamiento cuando un proveedor no tiene empresa registrada.

Los tests del backend han finalizado correctamente en las comprobaciones realizadas durante el desarrollo.

## 15. Pruebas funcionales e integración

Además de pytest, se han realizado peticiones HTTP reales entre los microservicios.

Entre los flujos comprobados se encuentran:

- Registro y autenticación de usuarios.
- Generación y validación de tokens JWT.
- Permisos de administrador, proveedor y cliente.
- Registro y consulta de empresas proveedoras.
- Comunicación de Proveedores con Autenticación.
- Creación y consulta de eventos.
- Publicación de espacios asociados a eventos.
- Registro y consulta de propuestas.
- Comunicación de Proveedores con Eventos.
- Creación y consulta de artistas.
- Creación de productos con variantes y existencias.
- Registro de pedidos.
- Actualización del stock después de una compra.

También se ha probado la aplicación frontend utilizando cuentas con distintos roles.

Se han comprobado el acceso administrativo, la consulta de la empresa del proveedor, sus propuestas y las restricciones aplicadas a clientes.

Las operaciones de tienda e historial de pedidos se han probado con datos almacenados en PostgreSQL.

Por último, el frontend ha superado las comprobaciones `npm run lint` y `npm run build`.

Estas comprobaciones verifican los flujos indicados, aunque no constituyen una batería exhaustiva de pruebas de seguridad, rendimiento o despliegue.

## 16. Estado del proyecto

Las principales funcionalidades de los cinco microservicios y del frontend se encuentran integradas en la rama `main`.

El backend dispone de persistencia PostgreSQL, autenticación, control de permisos y pruebas automatizadas.

El frontend permite utilizar los principales flujos de consulta, autenticación, comercio y proveedores.

Durante las primeras tres semanas de la Práctica 2 se han desarrollado la arquitectura, la lógica de negocio, la persistencia, la interfaz y las pruebas principales.

La cuarta semana se dedica a corregir incidencias, revisar el cumplimiento de los requisitos y completar la documentación.

El proyecto se ejecuta actualmente como entorno de desarrollo local. No se documenta como despliegue de producción.

## 17. Buenas prácticas

- Utilizar ramas de trabajo para nuevas funcionalidades y coordinar las integraciones en `main`.
- No subir contraseñas ni archivos `.env`.
- Mantener separados los datos reales y los datos de prueba.
- Ejecutar los tests sobre las bases de datos `_test`.
- Comprobar ESLint y la compilación del frontend.
- Revisar los cambios antes de realizar commits.
- Mantener actualizados los contratos OpenAPI.
- Evitar sobrescribir implementaciones al regenerar código.
- Documentar las nuevas funcionalidades y sus requisitos de ejecución.

## 18. Repositorio

Código fuente:

https://github.com/amansoba/PracticaASEE

Proyecto desarrollado en el contexto de la asignatura ASEE.
