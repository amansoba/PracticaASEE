export interface Cancion {
  id: string;
  artist_id: string;
  title: string;
  spotify_id?: string | null;
  spotify_url?: string | null;
  preview_url?: string | null;
}

export interface DatosCancion {
  title: string;
  spotify_id?: string;
  spotify_url?: string;
  preview_url?: string;
}

async function request<T>(path: string, token?: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init?.body) headers.set("Content-Type", "application/json");
  const response = await fetch(`/api/catalogo${path}`, { ...init, headers });
  if (!response.ok) throw new Error(response.status === 403 ? "Se requieren permisos de administrador" : "No se pudo completar la operación");
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const obtenerCanciones = (artistId: string) => request<Cancion[]>(`/artists/${encodeURIComponent(artistId)}/songs`);
export const crearCancion = (artistId: string, datos: DatosCancion, token: string) => request<Cancion>(`/artists/${encodeURIComponent(artistId)}/songs`, token, { method: "POST", body: JSON.stringify(datos) });
