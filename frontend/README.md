
# Subsonic Festival - Frontend

Aplicación web de Subsonic Festival, desarrollada con React, TypeScript y Vite para la Práctica 2 de ASEE.

El frontend proporciona una interfaz para utilizar las principales funcionalidades de los microservicios del proyecto.

## 1. Tecnologías

- React
- TypeScript
- Vite
- React Router
- CSS
- Fetch API
- ESLint

## 2. Requisitos previos

Para ejecutar el frontend se necesita:

- Node.js y npm.
- El repositorio de Subsonic Festival.
- Los microservicios FastAPI configurados.
- PostgreSQL iniciado.

El frontend puede arrancar por separado, pero para consultar y modificar datos reales es necesario que los microservicios estén funcionando.

## 3. Instalación

Desde la raíz del repositorio:

```powershell
cd frontend
npm install
```

Este comando instala las dependencias definidas en `package.json`.

La carpeta `node_modules` no se incluye en GitHub.

## 4. Ejecución

Desde `frontend`:

```powershell
npm run dev
```

Abrir en el navegador:

http://localhost:5173

Para detener el servidor de desarrollo:

```text
Ctrl + C
```

## 5. Microservicios necesarios

El frontend se comunica con cinco servicios:

| Servicio | Puerto |
|---|---|
| Autenticación | 8001 |
| Eventos | 8002 |
| Catálogo Musical | 8003 |
| Comercio | 8004 |
| Proveedores | 8005 |

Los servicios deben estar iniciados para utilizar todas las funcionalidades.

El proxy de Vite está definido en `vite.config.ts`.

## 6. Rutas de la aplicación

| Ruta | Funcionalidad |
|---|---|
| `/` | Página de inicio |
| `/eventos` | Consulta de eventos |
| `/artistas` | Catálogo de artistas |
| `/tienda` | Productos y compras |
| `/login` | Inicio de sesión |
| `/registro` | Registro de usuarios |
| `/mis-pedidos` | Historial de pedidos |
| `/proveedores` | Panel de proveedores y administración |

Las opciones de navegación dependen de la sesión del usuario.

## 7. Autenticación

El frontend se comunica con el microservicio de Autenticación.

El inicio de sesión devuelve un token JWT y los datos del usuario.

La aplicación mantiene la sesión en React mediante `AuthProvider` y almacena los datos necesarios en `sessionStorage`.

La implementación del contexto se encuentra en:

```text
src/context/
├── AuthContext.tsx
├── AuthContextBase.ts
└── useAuth.ts
```

Los componentes utilizan el hook `useAuth` para consultar el usuario autenticado, el token y las funciones de gestión de sesión.

Los roles disponibles son:

- `client`: cliente.
- `provider`: proveedor.
- `admin`: administrador.

Las restricciones de la interfaz complementan las comprobaciones de autorización realizadas por el backend.

Los permisos no dependen únicamente de React.

## 8. Funcionalidades

### Inicio

Página principal de Subsonic Festival con navegación hacia las secciones del sistema.

### Eventos

Consulta los eventos registrados mediante el microservicio de Gestión de Eventos.

### Artistas

Muestra información del catálogo musical obtenida desde el microservicio correspondiente.

### Tienda

Permite:

- Consultar productos de merchandising.
- Seleccionar talla y cantidad.
- Introducir la dirección de envío.
- Realizar pedidos autenticados.
- Mostrar el resultado de la compra.

El backend verifica las operaciones y actualiza las existencias de los productos.

### Mis pedidos

Los usuarios autenticados pueden consultar su historial de compras.

La información procede del microservicio de Comercio.

### Proveedores

La página `/proveedores` cambia en función del rol:

**Administrador**

Puede consultar el listado de empresas proveedoras registradas.

**Proveedor**

Puede consultar los datos de su empresa y las propuestas asociadas.

La aplicación utiliza:

```text
GET /providers/me
GET /requests/provider/{providerId}
```

El identificador de la empresa se obtiene desde el backend a partir de la sesión autenticada.

**Cliente**

No tiene acceso al panel de gestión de proveedores.

**Usuario sin sesión**

Debe iniciar sesión para acceder a las funcionalidades protegidas.

## 9. Estructura del código

```text
frontend/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   │   └── Navbar.tsx
│   ├── context/
│   │   ├── AuthContext.tsx
│   │   ├── AuthContextBase.ts
│   │   └── useAuth.ts
│   ├── pages/
│   │   ├── Artistas.tsx
│   │   ├── Eventos.tsx
│   │   ├── Login.tsx
│   │   ├── MisPedidos.tsx
│   │   ├── Proveedores.tsx
│   │   ├── Registro.tsx
│   │   └── Tienda.tsx
│   ├── services/
│   │   ├── artistas.ts
│   │   ├── auth.ts
│   │   ├── eventos.ts
│   │   ├── proveedores.ts
│   │   └── tienda.ts
│   ├── App.css
│   ├── App.tsx
│   ├── index.css
│   └── main.tsx
├── eslint.config.js
├── index.html
├── package.json
├── package-lock.json
├── tsconfig.app.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
└── README.md
```

### Componentes

`Navbar.tsx` contiene la barra de navegación y las opciones asociadas a la sesión.

### Contexto

Los archivos de `context` gestionan el estado de autenticación compartido entre componentes.

### Páginas

Los archivos de `pages` implementan las pantallas de la aplicación.

### Servicios

Los archivos de `services` concentran las peticiones HTTP realizadas a las APIs.

Esta separación permite mantener la lógica de comunicación fuera de los componentes visuales.

## 10. Configuración del proxy

El archivo `vite.config.ts` configura las rutas utilizadas por el frontend.

| Prefijo | Destino |
|---|---|
| `/api/auth` | http://127.0.0.1:8001 |
| `/api/eventos` | http://127.0.0.1:8002 |
| `/api/catalogo` | http://127.0.0.1:8003 |
| `/api/tienda` | http://127.0.0.1:8004 |
| `/api/proveedores` | http://127.0.0.1:8005 |

Cada ruta elimina su prefijo antes de enviar la petición al microservicio.

Por ejemplo:

```text
Frontend:
GET /api/eventos/events

Backend:
GET http://127.0.0.1:8002/events
```

Este proxy se utiliza en el entorno de desarrollo de Vite.

## 11. Comprobaciones de calidad

Desde la carpeta `frontend`:

### ESLint

```powershell
npm run lint
```

Analiza los archivos del proyecto para detectar problemas relacionados con las reglas configuradas de JavaScript, TypeScript y React.

### Compilación

```powershell
npm run build
```

Ejecuta la comprobación de TypeScript y genera la versión compilada del frontend.

Los archivos resultantes se guardan en `dist`.

Durante el desarrollo se han corregido los errores detectados por ESLint y se ha comprobado que ambos comandos finalizan correctamente.

## 12. Pruebas funcionales realizadas

Se han probado manualmente los siguientes flujos:

- Consulta de eventos.
- Consulta de artistas.
- Registro de usuarios.
- Inicio y cierre de sesión.
- Consulta de productos.
- Compra de merchandising.
- Consulta del historial de pedidos.
- Consulta del panel administrativo.
- Consulta de empresa y propuestas del proveedor.
- Restricción de acceso para usuarios con rol cliente.
- Cambio de sesión entre usuarios con roles diferentes.

Las operaciones se han realizado contra las APIs FastAPI y utilizando datos persistidos en PostgreSQL.

El backend dispone de pruebas automatizadas con pytest.

En esta fase no se incluye una batería automatizada específica de componentes React.

## 13. Consideraciones de seguridad

Las peticiones a endpoints protegidos utilizan el token JWT de la sesión.

Los permisos se comprueban en el backend, incluso cuando el frontend oculta las opciones no disponibles para un rol.

La sesión se mantiene en `sessionStorage` durante el uso de la aplicación.

Para un despliegue en producción sería necesario revisar el mecanismo de almacenamiento de tokens, la protección frente a XSS, la configuración HTTPS y otras medidas de seguridad.

El sistema está preparado para su utilización y comprobación en un entorno de desarrollo local.

## 14. Estado del frontend

Las principales funcionalidades de consulta, autenticación, compra e interacción con proveedores están implementadas y conectadas a los microservicios.

El frontend ha superado las comprobaciones de ESLint y compilación.

Durante la fase final del proyecto se revisan posibles incidencias, requisitos pendientes y documentación.

No todas las operaciones administrativas del backend disponen de una pantalla específica en el frontend.

## 15. Repositorio

El frontend forma parte del repositorio principal de Subsonic Festival:

https://github.com/amansoba/PracticaASEE

La versión integrada del proyecto se encuentra en la rama `main`.
