import { api } from "./api";

export interface VarianteProducto {
  size: string;
  stock: number;
}

export interface Producto {
  id: string;
  name: string;
  description: string | null;
  category: string;
  price: number;
  images: string[];
  variants: VarianteProducto[];
}

export interface ArticuloPedido {
  product_id: string;
  size: string;
  quantity: number;
  unit_price: number;
}

export interface DatosPedido {
  user_id: string;
  items: ArticuloPedido[];
  shipping_address: string;
  payment_method_id?: string;
}

export interface Pedido {
  id: string;
  user_id: string;
  items: ArticuloPedido[];
  total_price: number;
  status: string;
  created_at: string;
}

export async function obtenerProductos(): Promise<Producto[]> {
  return api.get("/api/tienda/products");
}

export async function obtenerProducto(id: string): Promise<Producto> {
  return api.get(`/api/tienda/products/${encodeURIComponent(id)}`);
}

export async function crearPedido(datos: DatosPedido): Promise<Pedido> {
  return api.post("/api/tienda/orders", datos);
}

export async function obtenerPedidosUsuario(
  userId: string
): Promise<Pedido[]> {
  return api.get(`/api/tienda/orders/user/${encodeURIComponent(userId)}`);
}

export async function obtenerPedido(id: string): Promise<Pedido> {
  return api.get(`/api/tienda/orders/${encodeURIComponent(id)}`);
}

export async function actualizarEstadoPedido(
  id: string,
  status: string
): Promise<void> {
  return api.put(`/api/tienda/orders/${encodeURIComponent(id)}/status`, {
    status,
  });
}

export async function cancelarPedido(id: string): Promise<void> {
  return api.post(`/api/tienda/orders/${encodeURIComponent(id)}/cancel`, {});
}
