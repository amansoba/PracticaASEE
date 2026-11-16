import { api } from "./api";

export interface Artista {
  id: string;
  name: string;
  genre: string;
  biography: string | null;
  image_url: string | null;
}

export async function obtenerArtistas(): Promise<Artista[]> {
  return api.get("/api/catalogo/artists");
}

export async function obtenerArtista(id: string): Promise<Artista> {
  return api.get(`/api/catalogo/artists/${encodeURIComponent(id)}`);
}
