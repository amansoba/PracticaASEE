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

export async function obtenerProveedores(): Promise<Proveedor[]> {
  return api.get("/api/proveedores/providers");
}

export async function crearProveedor(
  datos: DatosProveedor
): Promise<Proveedor> {
  return api.post("/api/proveedores/providers", datos);
}

export async function obtenerMiEmpresa(): Promise<Proveedor> {
  return api.get("/api/proveedores/providers/me");
}

export async function obtenerProveedor(id: string): Promise<Proveedor> {
  return api.get(`/api/proveedores/providers/${encodeURIComponent(id)}`);
}

export async function obtenerPropuestasProveedor(
  providerId: string
): Promise<PropuestaProveedor[]> {
  return api.get(
    `/api/proveedores/requests/provider/${encodeURIComponent(providerId)}`
  );
}
