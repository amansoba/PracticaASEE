
export interface Artista {
  id: string;
  name: string;
  genre: string;
  biography: string | null;
  image_url: string | null;
}

export interface DatosArtista {
  name: string;
  genre: string;
  biography?: string | null;
  image_url?: string | null;
}

export interface FiltrosArtistas {
  search?: string;
  genre?: string;
}

async function lanzarError(
  respuesta: Response,
  mensajePorDefecto: string
): Promise<never> {
  if (respuesta.status === 401) {
    throw new Error("Tu sesión no es válida o ha caducado");
  }

  if (respuesta.status === 403) {
    throw new Error("Se requieren permisos de administrador");
  }

  if (respuesta.status === 404) {
    throw new Error("El artista no existe");
  }

  if (respuesta.status === 503) {
    throw new Error("El servicio no está disponible temporalmente");
  }

  let cuerpo: unknown;

  try {
    cuerpo = await respuesta.json();
  } catch {
    throw new Error(mensajePorDefecto);
  }

  if (
    typeof cuerpo === "object" &&
    cuerpo !== null &&
    "detail" in cuerpo &&
    typeof cuerpo.detail === "string"
  ) {
    throw new Error(cuerpo.detail);
  }

  throw new Error(mensajePorDefecto);
}

function crearCabecerasAutenticadas(token: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

export async function obtenerArtistas(
  filtros: FiltrosArtistas = {}
): Promise<Artista[]> {
  const parametros = new URLSearchParams();

  if (filtros.search?.trim()) {
    parametros.set("search", filtros.search.trim());
  }

  if (filtros.genre?.trim()) {
    parametros.set("genre", filtros.genre.trim());
  }

  const consulta = parametros.toString();
  const respuesta = await fetch(
    consulta ? `/api/catalogo/artists?${consulta}` : "/api/catalogo/artists"
  );

  if (!respuesta.ok) {
    await lanzarError(respuesta, "No se pudieron cargar los artistas");
  }

  return respuesta.json() as Promise<Artista[]>;
}

export async function obtenerArtista(id: string): Promise<Artista> {
  const respuesta = await fetch(
    `/api/catalogo/artists/${encodeURIComponent(id)}`
  );

  if (!respuesta.ok) {
    await lanzarError(respuesta, "No se pudo cargar el artista");
  }

  return respuesta.json() as Promise<Artista>;
}

export async function crearArtista(
  datos: DatosArtista,
  token: string
): Promise<Artista> {
  const respuesta = await fetch("/api/catalogo/artists", {
    method: "POST",
    headers: crearCabecerasAutenticadas(token),
    body: JSON.stringify(datos),
  });

  if (!respuesta.ok) {
    await lanzarError(respuesta, "No se pudo crear el artista");
  }

  return respuesta.json() as Promise<Artista>;
}

export async function actualizarArtista(
  id: string,
  datos: DatosArtista,
  token: string
): Promise<Artista> {
  const respuesta = await fetch(
    `/api/catalogo/artists/${encodeURIComponent(id)}`,
    {
      method: "PUT",
      headers: crearCabecerasAutenticadas(token),
      body: JSON.stringify(datos),
    }
  );

  if (!respuesta.ok) {
    await lanzarError(respuesta, "No se pudo actualizar el artista");
  }

  return respuesta.json() as Promise<Artista>;
}

export async function eliminarArtista(
  id: string,
  token: string
): Promise<void> {
  const respuesta = await fetch(
    `/api/catalogo/artists/${encodeURIComponent(id)}`,
    {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!respuesta.ok) {
    await lanzarError(respuesta, "No se pudo eliminar el artista");
  }
}
