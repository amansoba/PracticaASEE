# Matriz de endpoints existentes

Contratos fuente contrastados con FastAPI tras integrar las dos ramas.
Cada fila corresponde a una operacion HTTP.

| Servicio | Negocio | Salud | Total |
|---|---:|---:|---:|
| auth-service | 10 | 2 | 12 |
| catalog-service | 9 | 2 | 11 |
| event-service | 12 | 2 | 14 |
| commerce-service | 12 | 2 | 14 |
| provider-service | 16 | 2 | 18 |
| **Total** | **59** | **10** | **69** |

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
| PUT | `/artists/{artistId}/songs/{songId}` | `updateSong` |
| DELETE | `/artists/{artistId}/songs/{songId}` | `deleteSong` |

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
| POST | `/tickets/validate` | `validateTicket` |

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
| GET | `/orders` | `listAllOrders` |
| GET | `/orders/user/{userId}` | `getOrdersByUser` |
| GET | `/orders/{id}` | `getOrderById` |
| PUT | `/orders/{id}/status` | `updateOrderStatus` |
| POST | `/orders/{id}/cancel` | `cancelOrder` |
| POST | `/orders/{id}/pay` | `payOrder` |

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
| PUT | `/external-services/{id}` | `updateExternalService` |
| DELETE | `/external-services/{id}` | `deleteExternalService` |
| PUT | `/spaces/{id}` | `updateSpace` |
| DELETE | `/spaces/{id}` | `deleteSpace` |
