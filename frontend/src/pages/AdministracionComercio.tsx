/* eslint-disable react-hooks/set-state-in-effect, react-hooks/exhaustive-deps */
import { useEffect, useState, type FormEvent } from "react";
import { useAuth } from "../context/useAuth";
import {
  actualizarEstadoPedido, actualizarProducto, crearProducto, eliminarProducto,
  obtenerPedido, obtenerProductosAdmin, type DatosProducto,
} from "../services/comercioAdmin";
import type { Pedido, Producto, VarianteProducto } from "../services/tienda";

const estados = ["pending", "paid", "preparing", "shipped", "delivered", "cancelled"] as const;
type EstadoPedido = (typeof estados)[number];
const productoInicial: DatosProducto = { name: "", description: "", category: "", price: 0, images: [], variants: [] };

function urlsValidas(urls: string[]): boolean {
  return urls.every((url) => URL.canParse(url));
}

export default function AdministracionComercio() {
  const { usuario, token } = useAuth();
  const [productos, setProductos] = useState<Producto[]>([]);
  const [form, setForm] = useState<DatosProducto>(productoInicial);
  const [editando, setEditando] = useState<string | null>(null);
  const [nuevaTalla, setNuevaTalla] = useState("");
  const [nuevoStock, setNuevoStock] = useState(0);
  const [pedidoId, setPedidoId] = useState("");
  const [pedido, setPedido] = useState<Pedido | null>(null);
  const [estado, setEstado] = useState<EstadoPedido>("pending");
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  async function cargarProductos() {
    if (!token) return;
    setCargando(true);
    try {
      setProductos(await obtenerProductosAdmin(token));
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudieron cargar los productos.");
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    void cargarProductos();
  }, [token]);

  function actualizarVariante(index: number, cambio: Partial<VarianteProducto>) {
    const variantes = [...(form.variants ?? [])];
    variantes[index] = { ...variantes[index], ...cambio };
    setForm({ ...form, variants: variantes });
  }

  function añadirVariante() {
    const talla = nuevaTalla.trim();
    if (!talla || nuevoStock < 0) {
      setError("La talla es obligatoria y el stock no puede ser negativo.");
      return;
    }
    if (form.variants?.some((variante) => variante.size.toLowerCase() === talla.toLowerCase())) {
      setError("No puede haber dos variantes con la misma talla.");
      return;
    }
    setForm({ ...form, variants: [...(form.variants ?? []), { size: talla, stock: nuevoStock }] });
    setNuevaTalla("");
    setNuevoStock(0);
    setError("");
  }

  async function guardarProducto(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const imagenes = (form.images ?? []).map((image) => image.trim()).filter(Boolean);
    if (!token || !form.name.trim() || !form.category.trim() || form.price <= 0) {
      setError("Nombre, categoría y un precio positivo son obligatorios.");
      return;
    }
    if ((form.variants ?? []).some((variante) => !variante.size.trim() || variante.stock < 0)) {
      setError("Todas las variantes deben tener talla y stock no negativo.");
      return;
    }
    const normalizadas = (form.variants ?? []).map((variante) => variante.size.trim().toLowerCase());
    if (new Set(normalizadas).size !== normalizadas.length) {
      setError("No puede haber tallas duplicadas.");
      return;
    }
    if (!urlsValidas(imagenes)) {
      setError("Todas las imágenes deben ser URLs válidas.");
      return;
    }
    setGuardando(true);
    try {
      const datos = { ...form, images: imagenes };
      if (editando) await actualizarProducto(editando, datos, token); else await crearProducto(datos, token);
      setMensaje(editando ? "Producto actualizado correctamente." : "Producto creado correctamente.");
      setForm(productoInicial);
      setEditando(null);
      await cargarProductos();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo guardar el producto.");
    } finally {
      setGuardando(false);
    }
  }

  async function borrarProducto(id: string) {
    if (!token || !window.confirm("¿Seguro que quieres eliminar este producto?")) return;
    try { await eliminarProducto(id, token); setMensaje("Producto eliminado correctamente."); await cargarProductos(); } catch (err) { setError(err instanceof Error ? err.message : "No se pudo eliminar el producto."); }
  }

  async function consultarPedido(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPedido(null);
    setError("");
    if (!token || !pedidoId.trim()) { setError("Introduce el identificador del pedido."); return; }
    try {
      const dato = await obtenerPedido(pedidoId.trim(), token);
      setPedido(dato);
      setEstado(estados.includes(dato.status as EstadoPedido) ? dato.status as EstadoPedido : "pending");
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo cargar el pedido.");
    }
  }

  async function cambiarEstado() {
    if (!token || !pedido) return;
    try { setPedido(await actualizarEstadoPedido(pedido.id, estado, token)); setMensaje("Estado del pedido actualizado."); } catch (err) { setError(err instanceof Error ? err.message : "No se pudo actualizar el estado."); }
  }

  if (!usuario || usuario.role !== "admin" || !token) return <main className="pagina-eventos"><h1>Administración de comercio</h1><p role="alert">Se requieren permisos de administrador.</p></main>;

  return <main className="pagina-eventos"><div className="eventos-encabezado"><p className="subtitulo">ADMINISTRACIÓN</p><h1>Comercio</h1><p>Productos, variantes, stock y consulta individual de pedidos.</p></div>{mensaje && <p role="status">{mensaje}</p>}{error && <p role="alert">{error}</p>}
    <section className="admin-seccion"><h2>{editando ? "Editar producto" : "Nuevo producto"}</h2><form className="admin-form" onSubmit={(event) => void guardarProducto(event)}><label>Nombre<input required value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} /></label><label>Categoría<input required value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value })} /></label><label>Descripción<input value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} /></label><label>Precio<input required min="0.01" step="0.01" type="number" value={form.price} onChange={(event) => setForm({ ...form, price: Number(event.target.value) })} /></label><label>Imágenes<input placeholder="https://... , https://..." value={(form.images ?? []).join(", ")} onChange={(event) => setForm({ ...form, images: event.target.value.split(",").map((value) => value.trim()).filter(Boolean) })} /></label><div><h3>Variantes y stock</h3>{(form.variants ?? []).map((variante, index) => <div key={`${variante.size}-${index}`}><input aria-label={`Talla ${index + 1}`} value={variante.size} onChange={(event) => actualizarVariante(index, { size: event.target.value })} /><input aria-label={`Stock ${index + 1}`} type="number" min="0" value={variante.stock} onChange={(event) => actualizarVariante(index, { stock: Number(event.target.value) })} /><button type="button" onClick={() => setForm({ ...form, variants: form.variants?.filter((_, itemIndex) => itemIndex !== index) })}>Quitar</button></div>)}<input aria-label="Nueva talla" placeholder="Talla" value={nuevaTalla} onChange={(event) => setNuevaTalla(event.target.value)} /><input aria-label="Nuevo stock" type="number" min="0" value={nuevoStock} onChange={(event) => setNuevoStock(Number(event.target.value))} /><button type="button" onClick={añadirVariante}>Añadir variante</button></div><button type="submit" disabled={guardando}>{guardando ? "Guardando..." : "Guardar producto"}</button></form></section>
    <section className="admin-seccion"><h2>Productos</h2>{cargando ? <p role="status">Cargando productos...</p> : productos.length === 0 ? <p>No hay productos.</p> : <div className="admin-tabla">{productos.map((producto) => <article className="evento-card" key={producto.id}><div className="evento-card-contenido"><h3>{producto.name}</h3><p>{producto.category} · {producto.price.toFixed(2)} €</p><p>{producto.variants.map((variante) => `${variante.size}: ${variante.stock}`).join(" · ")}</p><button type="button" onClick={() => { setEditando(producto.id); setForm({ name: producto.name, description: producto.description ?? "", category: producto.category, price: producto.price, images: producto.images, variants: producto.variants }); }}>Editar</button>{" "}<button type="button" onClick={() => void borrarProducto(producto.id)}>Eliminar</button></div></article>)}</div>}</section>
    <section className="admin-seccion"><h2>Consultar pedido</h2><form className="admin-form" onSubmit={(event) => void consultarPedido(event)}><label>ID de pedido<input required value={pedidoId} onChange={(event) => setPedidoId(event.target.value)} /></label><button type="submit">Consultar</button></form>{pedido && <div><p>Pedido {pedido.id} · {pedido.total_price.toFixed(2)} €</p><ul>{pedido.items.map((item, index) => <li key={`${item.product_id}-${index}`}>{item.product_id} · talla {item.size} · {item.quantity} unidades</li>)}</ul><select aria-label="Estado del pedido" value={estado} onChange={(event) => setEstado(event.target.value as EstadoPedido)}>{estados.map((item) => <option key={item} value={item}>{item}</option>)}</select><button type="button" onClick={() => void cambiarEstado()}>Actualizar estado</button></div>}</section>
  </main>;
}
