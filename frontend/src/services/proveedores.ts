
import { api } from "./api";

export interface Proveedor {
  id: string;
  user_id: string;
  company_name: string;
  cif_nif: string;
  service_category: string;
  contact_email: string;
}

export interface DatosProveedor {
  user_id: string;
  company_name: string;
  cif_nif: string;
  service_category: string;
  contact_email: string;
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

export interface MiEmpresaProveedor {
  id: string;
  user_id: string;
  company_name: string;
  cif_nif: string;
  service_category: string;
  contact_email: string | null;
}

export class ProveedorApiError extends Error {
  public readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ProveedorApiError";
    this.status = status;
  }
}

// Listar proveedores: compatible con Borja y Álvaro.
export async function obtenerProveedores(
  token?: string
): Promise<Proveedor[]> {
  if (!token) {
    return api.get<Proveedor[]>("/api/proveedores/providers");
  }

  const respuesta = await fetch("/api/proveedores/providers", {
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

  return respuesta.json() as Promise<Proveedor[]>;
}

// Crear una empresa: funcionalidad incorporada por Álvaro.
export async function crearProveedor(
  datos: DatosProveedor
): Promise<Proveedor> {
  return api.post<Proveedor>("/api/proveedores/providers", datos);
}

// Consultar empresa propia: conserva errores HTTP de Borja.
export async function obtenerMiEmpresa(
  token?: string
): Promise<MiEmpresaProveedor> {
  if (!token) {
    return api.get<MiEmpresaProveedor>(
      "/api/proveedores/providers/me"
    );
  }

  const respuesta = await fetch(
    "/api/proveedores/providers/me",
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!respuesta.ok) {
    if (respuesta.status === 401) {
      throw new ProveedorApiError(
        401,
        "Tu sesión no es válida o ha caducado"
      );
    }

    if (respuesta.status === 403) {
      throw new ProveedorApiError(
        403,
        "No tienes permisos de proveedor"
      );
    }

    if (respuesta.status === 404) {
      throw new ProveedorApiError(
        404,
        "Todavía no tienes una empresa registrada"
      );
    }

    throw new ProveedorApiError(
      respuesta.status,
      "No se pudo consultar tu empresa"
    );
  }

  return respuesta.json() as Promise<MiEmpresaProveedor>;
}

// Consultar detalles de un proveedor.
export async function obtenerProveedor(
  id: string
): Promise<Proveedor> {
  return api.get<Proveedor>(
    `/api/proveedores/providers/${encodeURIComponent(id)}`
  );
}

// Consultar propuestas: compatible con ambas implementaciones.
export async function obtenerPropuestasProveedor(
  providerId: string,
  token?: string
): Promise<PropuestaProveedor[]> {
  const ruta =
    `/api/proveedores/requests/provider/${encodeURIComponent(providerId)}`;

  if (!token) {
    return api.get<PropuestaProveedor[]>(ruta);
  }

  const respuesta = await fetch(ruta, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!respuesta.ok) {
    if (respuesta.status === 401) {
      throw new Error("Tu sesión no es válida o ha caducado");
    }

    if (respuesta.status === 403) {
      throw new Error(
        "No tienes permiso para consultar estas propuestas"
      );
    }

    if (respuesta.status === 404) {
      throw new Error("La empresa proveedora no existe");
    }

    throw new Error("No se pudieron cargar las propuestas");
  }

  return respuesta.json() as Promise<PropuestaProveedor[]>;
}
