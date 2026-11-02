
export interface Evento {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  venue: string;
  location_city: string;
}

export async function obtenerEventos(): Promise<Evento[]> {
  const respuesta = await fetch("/api/eventos/events");

  if (!respuesta.ok) {
    throw new Error("No se pudieron cargar los eventos");
  }

  return respuesta.json();
}
