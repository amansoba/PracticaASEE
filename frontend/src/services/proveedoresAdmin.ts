import type { Evento } from "./eventos";
import type { MiEmpresaProveedor, Proveedor, PropuestaProveedor } from "./proveedores";

export interface ServicioExterno { id: string; name: string; description?: string | null; }
export interface Espacio { id: string; event_id: string; name: string; dimensions?: string | null; base_price: number; is_available: boolean; }
export interface DatosProveedor { user_id: string; company_name: string; cif_nif: string; service_category: string; contact_email: string; }
export interface DatosServicio { name: string; description?: string; }
export interface DatosEspacio { event_id: string; name: string; dimensions?: string; base_price: number; is_available: boolean; }
export interface DatosPropuesta { space_id: string; provider_id: string; event_id: string; budget_proposal: number; setup_date?: string; }

async function request<T>(path: string, token?: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init?.body) headers.set("Content-Type", "application/json");
  const response = await fetch(`/api/proveedores${path}`, { ...init, headers });
  if (!response.ok) throw new Error(response.status === 403 ? "No tienes permisos para esta operación" : response.status === 404 ? "Recurso no encontrado" : "No se pudo completar la operación");
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const obtenerProveedor = (id: string, token: string) => request<Proveedor>(`/providers/${encodeURIComponent(id)}`, token);
export const crearProveedor = (datos: DatosProveedor, token: string) => request<MiEmpresaProveedor>("/providers", token, { method: "POST", body: JSON.stringify(datos) });
export const obtenerServicios = () => request<ServicioExterno[]>("/external-services");
export const crearServicio = (datos: DatosServicio, token: string) => request<ServicioExterno>("/external-services", token, { method: "POST", body: JSON.stringify(datos) });
export const obtenerEspacios = (eventId: string) => request<Espacio[]>(`/spaces?event_id=${encodeURIComponent(eventId)}`);
export const crearEspacio = (datos: DatosEspacio, token: string) => request<Espacio>("/spaces", token, { method: "POST", body: JSON.stringify(datos) });
export const obtenerPropuestasEvento = (eventId: string, token: string) => request<PropuestaProveedor[]>(`/requests/event/${encodeURIComponent(eventId)}`, token);
export const actualizarEstadoPropuesta = (id: string, status: "approved" | "rejected", token: string) => request<PropuestaProveedor>(`/requests/${encodeURIComponent(id)}/status`, token, { method: "PUT", body: JSON.stringify({ status }) });
export const crearPropuesta = (datos: DatosPropuesta, token: string) => request<PropuestaProveedor>("/requests", token, { method: "POST", body: JSON.stringify(datos) });
export const obtenerMisPropuestas = (providerId: string, token: string) => request<PropuestaProveedor[]>(`/requests/provider/${encodeURIComponent(providerId)}`, token);
export type { Evento };
export type { PropuestaProveedor };

export const actualizarServicio = (
  id: string,
  datos: DatosServicio,
  token: string
) =>
  request<ServicioExterno>(
    `/external-services/${encodeURIComponent(id)}`,
    token,
    { method: "PUT", body: JSON.stringify(datos) }
  );

export const eliminarServicio = (
  id: string,
  token: string
) =>
  request<void>(
    `/external-services/${encodeURIComponent(id)}`,
    token,
    { method: "DELETE" }
  );

export const actualizarEspacio = (
  id: string,
  datos: DatosEspacio,
  token: string
) =>
  request<Espacio>(
    `/spaces/${encodeURIComponent(id)}`,
    token,
    { method: "PUT", body: JSON.stringify(datos) }
  );

export const eliminarEspacio = (
  id: string,
  token: string
) =>
  request<void>(
    `/spaces/${encodeURIComponent(id)}`,
    token,
    { method: "DELETE" }
  );
