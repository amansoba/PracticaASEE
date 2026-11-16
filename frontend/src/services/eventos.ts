import { api } from "./api";

export interface Evento {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  venue: string;
  location_city: string;
}

export interface Pase {
  id: string;
  event_id: string;
  type_name: string;
  price: number;
  capacity: number;
  available_tickets: number;
  benefits: string[];
}

export interface Actuacion {
  id: string;
  event_id: string;
  artist_id: string;
  artist_name: string;
  stage: string;
  start_time: string;
  end_time: string;
}

export interface Entrada {
  id: string;
  event_id: string;
  pass_id: string;
  user_id: string;
  qr_code: string;
  status: string;
  purchased_at: string;
}

export interface DatosEvento {
  name: string;
  start_date: string;
  end_date: string;
  venue: string;
  location_city: string;
}

export interface DatosPase {
  type_name: string;
  price: number;
  capacity: number;
  benefits?: string[];
}

export interface DatosActuacion {
  artist_id: string;
  artist_name: string;
  stage: string;
  start_time: string;
  end_time: string;
}

export interface DatosCompraEntrada {
  event_id: string;
  pass_id: string;
  user_id: string;
}

export async function obtenerEventos(): Promise<Evento[]> {
  return api.get("/api/eventos/events");
}

export async function obtenerEvento(id: string): Promise<Evento> {
  return api.get(`/api/eventos/events/${encodeURIComponent(id)}`);
}

export async function crearEvento(datos: DatosEvento): Promise<Evento> {
  return api.post("/api/eventos/events", datos);
}

export async function actualizarEvento(
  id: string,
  datos: DatosEvento
): Promise<Evento> {
  return api.put(`/api/eventos/events/${encodeURIComponent(id)}`, datos);
}

export async function eliminarEvento(id: string): Promise<void> {
  return api.delete(`/api/eventos/events/${encodeURIComponent(id)}`);
}

export async function obtenerPasesDeEvento(id: string): Promise<Pase[]> {
  return api.get(`/api/eventos/events/${encodeURIComponent(id)}/passes`);
}

export async function crearPase(
  eventoId: string,
  datos: DatosPase
): Promise<Pase> {
  return api.post(
    `/api/eventos/events/${encodeURIComponent(eventoId)}/passes`,
    datos
  );
}

export async function obtenerLineUp(id: string): Promise<Actuacion[]> {
  return api.get(`/api/eventos/events/${encodeURIComponent(id)}/lineup`);
}

export async function crearActuacion(
  eventoId: string,
  datos: DatosActuacion
): Promise<Actuacion> {
  return api.post(
    `/api/eventos/events/${encodeURIComponent(eventoId)}/lineup`,
    datos
  );
}

export async function comprarEntrada(
  datos: DatosCompraEntrada
): Promise<Entrada> {
  return api.post("/api/eventos/tickets/purchase", datos);
}

export async function obtenerEntradasDeUsuario(
  userId: string
): Promise<Entrada[]> {
  return api.get(
    `/api/eventos/tickets/user/${encodeURIComponent(userId)}`
  );
}
