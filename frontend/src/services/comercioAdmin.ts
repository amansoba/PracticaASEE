import type { Pedido, Producto, VarianteProducto } from "./tienda";

export interface DatosProducto {
  name: string;
  description?: string;
  category: string;
  price: number;
  images?: string[];
  variants?: VarianteProducto[];
}

async function request<T>(path: string, token?: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init?.body) headers.set("Content-Type", "application/json");
  const response = await fetch(`/api/tienda${path}`, { ...init, headers });
  if (!response.ok) throw new Error(response.status === 403 ? "Se requieren permisos de administrador" : "No se pudo completar la operación");
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const obtenerProductosAdmin = (token: string, category?: string) => request<Producto[]>(category ? `/products?category=${encodeURIComponent(category)}` : "/products", token);
export const obtenerProducto = (id: string, token: string) => request<Producto>(`/products/${encodeURIComponent(id)}`, token);
export const crearProducto = (datos: DatosProducto, token: string) => request<Producto>("/products", token, { method: "POST", body: JSON.stringify(datos) });
export const actualizarProducto = (id: string, datos: DatosProducto, token: string) => request<Producto>(`/products/${encodeURIComponent(id)}`, token, { method: "PUT", body: JSON.stringify(datos) });
export const eliminarProducto = (id: string, token: string) => request<void>(`/products/${encodeURIComponent(id)}`, token, { method: "DELETE" });
export const obtenerPedido = (id: string, token: string) => request<Pedido>(`/orders/${encodeURIComponent(id)}`, token);
export const actualizarEstadoPedido = (id: string, status: string, token: string) => request<Pedido>(`/orders/${encodeURIComponent(id)}/status`, token, { method: "PUT", body: JSON.stringify({ status }) });
