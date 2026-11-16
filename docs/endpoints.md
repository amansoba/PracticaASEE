# Matriz de endpoints existentes

Generada a partir de los contratos fuente y contrastada con FastAPI mediante
`python scripts/check_runtime_contracts.py`. Cada fila es una operación HTTP.
Los permisos y esquemas completos están en los contratos y Swagger.

| Servicio | Negocio | Salud | Total |
|---|---:|---:|---:|
| auth-service | 10 | 2 | 12 |
| catalog-service | 7 | 2 | 9 |
| event-service | 11 | 2 | 13 |
| commerce-service | 9 | 2 | 11 |
| provider-service | 12 | 2 | 14 |
| **Total** | **49** | **10** | **59** |

## auth-service

| Metodo | Ruta | operationId |
|---|---|---|
| GET | `/health` | `health` |
| GET | `/ready` | `ready` |
| POST | `/auth/register` | `registerUser` |
| POST | `/auth/login` | `loginUser` |
| POST | `/auth/logout` | `logoutUser` |
| POST | `/auth/reset-password` | `requestPasswordReset` |
| POST | `/auth/reset-password/confirm` | `confirmPasswordReset` |
| GET | `/users/me` | `getCurrentUserProfile` |
| PUT | `/users/me` | `updateCurrentUserProfile` |
| GET | `/users` | `listAllUsers` |
| GET | `/users/{id}` | `getUserById` |
| PUT | `/users/{id}/role` | `updateUserRole` |

## catalog-service

| Metodo | Ruta | operationId |
|---|---|---|
| GET | `/health` | `health` |
| GET | `/ready` | `ready` |
| GET | `/artists` | `getArtists` |
| POST | `/artists` | `createArtist` |
| GET | `/artists/{id}` | `getArtistById` |
| PUT | `/artists/{id}` | `updateArtist` |
| DELETE | `/artists/{id}` | `deleteArtist` |
| GET | `/artists/{id}/songs` | `getSongsByArtist` |
| POST | `/artists/{id}/songs` | `addSongToArtist` |

## event-service

| Metodo | Ruta | operationId |
|---|---|---|
| GET | `/health` | `health` |
| GET | `/ready` | `ready` |
| GET | `/events` | `getAllEvents` |
| POST | `/events` | `createEvent` |
| GET | `/events/{id}` | `getEventById` |
| PUT | `/events/{id}` | `updateEvent` |
| DELETE | `/events/{id}` | `deleteEvent` |
| GET | `/events/{id}/lineup` | `getEventLineup` |
| POST | `/events/{id}/lineup` | `addScheduleEntry` |
| GET | `/events/{id}/passes` | `getPassConfigsByEvent` |
| POST | `/events/{id}/passes` | `createPassConfig` |
| POST | `/tickets/purchase` | `purchaseTicket` |
| GET | `/tickets/user/{userId}` | `getTicketsByUser` |

## commerce-service

| Metodo | Ruta | operationId |
|---|---|---|
| GET | `/health` | `health` |
| GET | `/ready` | `ready` |
| GET | `/products` | `getProducts` |
| POST | `/products` | `createProduct` |
| GET | `/products/{id}` | `getProductById` |
| PUT | `/products/{id}` | `updateProduct` |
| DELETE | `/products/{id}` | `deleteProduct` |
| POST | `/orders` | `createOrder` |
| GET | `/orders/user/{userId}` | `getOrdersByUser` |
| GET | `/orders/{id}` | `getOrderById` |
| PUT | `/orders/{id}/status` | `updateOrderStatus` |

## provider-service

| Metodo | Ruta | operationId |
|---|---|---|
| GET | `/health` | `health` |
| GET | `/ready` | `ready` |
| GET | `/providers` | `getProviders` |
| POST | `/providers` | `createProvider` |
| GET | `/providers/me` | `getMyProvider` |
| GET | `/providers/{id}` | `getProviderById` |
| GET | `/external-services` | `getExternalServices` |
| POST | `/external-services` | `createExternalService` |
| GET | `/spaces` | `getSpacesByEvent` |
| POST | `/spaces` | `createSpace` |
| POST | `/requests` | `createSpaceProposal` |
| GET | `/requests/provider/{providerId}` | `getProposalsByProvider` |
| GET | `/requests/event/{eventId}` | `getProposalsByEvent` |
| PUT | `/requests/{id}/status` | `updateProposalStatus` |
