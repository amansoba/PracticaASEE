
export interface Proveedor {
  id: string;
  user_id: string;
  company_name: string;
  cif_nif: string;
  service_category: string;
  contact_email: string;
}

export async function obtenerProveedores(
  token: string
): Promise<Proveedor[]> {
  const respuesta = await fetch("/api/proveedores/providers", {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!respuesta.ok) {
    if (respuesta.status === 401) {
      throw new Error("Tu sesión ha caducado o no es válida");
    }

    if (respuesta.status === 403) {
      throw new Error("Se requieren permisos de administrador");
    }

    throw new Error("No se pudieron cargar los proveedores");
  }

  return respuesta.json();
}


export interface PropuestaProveedor {
  id: string;
  space_id: string;
  provider_id: string;
  event_id: string;
  budget_proposal: number;
  setup_date: string | null;
  status: string;
}

export async function obtenerPropuestasProveedor(
  providerId: string,
  token: string
): Promise<PropuestaProveedor[]> {
  const respuesta = await fetch(
    `/api/proveedores/requests/provider/${encodeURIComponent(providerId)}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!respuesta.ok) {
    if (respuesta.status === 401) {
      throw new Error("Tu sesión no es válida o ha caducado");
    }

    if (respuesta.status === 403) {
      throw new Error("No tienes permiso para consultar estas propuestas");
    }

    if (respuesta.status === 404) {
      throw new Error("La empresa proveedora no existe");
    }

    throw new Error("No se pudieron cargar las propuestas");
  }

  return respuesta.json();
}


export interface MiEmpresaProveedor {
  id: string;
  user_id: string;
  company_name: string;
  cif_nif: string;
  service_category: string;
  contact_email: string | null;
}

export async function obtenerMiEmpresa(
  token: string
): Promise<MiEmpresaProveedor> {
  const respuesta = await fetch("/api/proveedores/providers/me", {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!respuesta.ok) {
    if (respuesta.status === 401) {
      throw new Error("Tu sesión no es válida o ha caducado");
    }

    if (respuesta.status === 403) {
      throw new Error("No tienes permisos de proveedor");
    }

    if (respuesta.status === 404) {
      throw new Error("Todavía no tienes una empresa registrada");
    }

    throw new Error("No se pudo consultar tu empresa");
  }

  return respuesta.json();
}
