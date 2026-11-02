
export interface Artista {
  id: string;
  name: string;
  genre: string;
  biography: string | null;
  image_url: string | null;
}

export async function obtenerArtistas(): Promise<Artista[]> {
  const respuesta = await fetch("/api/catalogo/artists");

  if (!respuesta.ok) {
    throw new Error("No se pudieron cargar los artistas");
  }

  return respuesta.json();
}
