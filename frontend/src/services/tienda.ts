
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

export async function obtenerProductos(): Promise<Producto[]> {
  const respuesta = await fetch("/api/tienda/products");

  if (!respuesta.ok) {
    throw new Error("No se pudieron cargar los productos");
  }

  return respuesta.json();
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
}

export interface Pedido {
  id: string;
  user_id: string;
  items: ArticuloPedido[];
  total_price: number;
  status: string;
  created_at: string;
}

export async function crearPedido(
  datos: DatosPedido,
  token: string
): Promise<Pedido> {
  const respuesta = await fetch("/api/tienda/orders", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(datos),
  });

  if (!respuesta.ok) {
    if (respuesta.status === 401) {
      throw new Error("Debes iniciar sesión para comprar");
    }

    if (respuesta.status === 403) {
      throw new Error("No tienes permiso para realizar este pedido");
    }

    if (respuesta.status === 409) {
      throw new Error("No hay stock suficiente");
    }

    throw new Error("No se pudo registrar el pedido");
  }

  return respuesta.json();
}


export async function obtenerPedidosUsuario(
  userId: string,
  token: string
): Promise<Pedido[]> {
  const respuesta = await fetch(
    `/api/tienda/orders/user/${encodeURIComponent(userId)}`,
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
      throw new Error("No tienes permiso para consultar estos pedidos");
    }

    throw new Error("No se pudo cargar el historial de pedidos");
  }

  return respuesta.json();
}
