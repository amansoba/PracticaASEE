# Guion de demo – Flujo público, cliente y gestión de eventos

Este guion cubre la parte implementada por Álvaro en el frontend.

## Datos previos

Asegúrate de que el backend y PostgreSQL están arrancados y de que existe al
menos:

- Un usuario `admin`.
- Un usuario `client`.
- Algunos artistas y productos (se pueden crear desde Swagger o seed).

## 1. Flujo público

1. Abrir la aplicación en `http://localhost:5173`.
2. Desde el inicio, navegar a **Eventos**.
3. Pulsar sobre un evento para ver su detalle:
   - Información del festival.
   - Tipos de pase disponibles.
   - Line-up.
4. Navegar a **Artistas** para ver el catálogo musical.
5. Navegar a **Tienda** para ver productos de merchandising.

## 2. Flujo de cliente

1. Registrarse desde **Registro** con rol `client`.
2. Iniciar sesión.
3. En un evento con pases disponibles, pulsar **Comprar entrada**.
4. Ir a **Mis entradas** para ver la entrada comprada y su QR.
5. En **Tienda**, añadir productos al **Carrito** o usar **Comprar ahora**.
6. Desde el **Carrito**, introducir dirección y confirmar el pedido.
7. Ir a **Mis pedidos**, pulsar un pedido y, si está `pending`, pulsar
   **Cancelar pedido**.
8. Editar el perfil desde **Perfil**.
9. Probar la recuperación de contraseña desde **¿Has olvidado tu contraseña?**
   en el login.

## 3. Gestión de eventos (admin)

1. Iniciar sesión con el usuario `admin`.
2. Aparecen los enlaces **Admin eventos** y **Usuarios**.
3. En **Admin eventos**:
   - Crear un nuevo festival.
   - Editar o eliminar un evento existente.
   - Pulsar **Ver / gestionar** en un evento.
4. En la página de detalle del evento, como admin:
   - Crear un nuevo tipo de pase.
   - Añadir actuaciones al line-up.
5. En **Usuarios**, cambiar el rol de cualquier usuario (excepto el propio).

## Escenarios E2E recomendados

- Registro → login → compra de entrada → consulta en "Mis entradas".
- Login de cliente → añadir productos al carrito → checkout → ver pedido →
  cancelar pedido.
- Login de admin → crear evento → añadir pase y actuación → logout.
