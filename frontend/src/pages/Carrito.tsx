import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { crearPedido, obtenerProductos, type Producto } from "../services/tienda";

interface ItemCarrito {
  productId: string;
  name: string;
  size: string;
  quantity: number;
  unitPrice: number;
}

const CARRITO_KEY = "subsonic_carrito";

function leerCarrito(): ItemCarrito[] {
  try {
    const datos = sessionStorage.getItem(CARRITO_KEY);
    return datos ? (JSON.parse(datos) as ItemCarrito[]) : [];
  } catch {
    return [];
  }
}

function guardarCarrito(items: ItemCarrito[]) {
  sessionStorage.setItem(CARRITO_KEY, JSON.stringify(items));
}

export default function Carrito() {
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [items, setItems] = useState<ItemCarrito[]>(leerCarrito);
  const [productos, setProductos] = useState<Record<string, Producto>>({});
  const [direccion, setDireccion] = useState("");
  const [cargando, setCargando] = useState(true);
  const [procesando, setProcesando] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");

  useEffect(() => {
    async function cargarProductos() {
      try {
        const datos = await obtenerProductos();
        const mapa: Record<string, Producto> = {};
        datos.forEach((p) => (mapa[p.id] = p));
        setProductos(mapa);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error al cargar productos");
      } finally {
        setCargando(false);
      }
    }

    void cargarProductos();
  }, []);

  function actualizarCantidad(productId: string, size: string, cantidad: number) {
    if (cantidad < 1) {
      eliminarItem(productId, size);
      return;
    }
    const nuevos = items.map((it) =>
      it.productId === productId && it.size === size
        ? { ...it, quantity: cantidad }
        : it
    );
    setItems(nuevos);
    guardarCarrito(nuevos);
  }

  function eliminarItem(productId: string, size: string) {
    const nuevos = items.filter(
      (it) => !(it.productId === productId && it.size === size)
    );
    setItems(nuevos);
    guardarCarrito(nuevos);
  }

  async function confirmarPedido() {
    if (!usuario) {
      navigate("/login");
      return;
    }
    if (!direccion.trim()) {
      setError("La dirección de envío es obligatoria");
      return;
    }
    if (items.length === 0) {
      setError("El carrito está vacío");
      return;
    }

    setProcesando(true);
    setError("");

    try {
      const pedido = await crearPedido({
        user_id: usuario.id,
        shipping_address: direccion.trim(),
        items: items.map((it) => ({
          product_id: it.productId,
          size: it.size,
          quantity: it.quantity,
          unit_price: it.unitPrice,
        })),
      });
      guardarCarrito([]);
      setItems([]);
      setMensaje(`Pedido ${pedido.id} registrado. Total: ${pedido.total_price.toFixed(2)} €`);
      setTimeout(() => navigate(`/mis-pedidos/${pedido.id}`), 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al realizar el pedido");
    } finally {
      setProcesando(false);
    }
  }

  const total = items.reduce(
    (sum, it) => sum + it.unitPrice * it.quantity,
    0
  );

  if (!usuario) {
    return (
      <main className="pagina-eventos">
        <h1>Carrito</h1>
        <p>Debes iniciar sesión para ver el carrito.</p>
        <Link to="/login" className="navbar-login">Iniciar sesión</Link>
      </main>
    );
  }

  return (
    <main className="pagina-eventos">
      <div className="eventos-encabezado">
        <p className="subtitulo">TU COMPRA</p>
        <h1>Carrito</h1>
      </div>

      {cargando && <p>Cargando...</p>}
      {error && <p className="login-error">{error}</p>}
      {mensaje && <p className="registro-exito">{mensaje}</p>}

      {!cargando && items.length === 0 && !mensaje && (
        <p>El carrito está vacío. <Link to="/tienda">Ir a la tienda</Link></p>
      )}

      {items.length > 0 && (
        <>
          <div className="eventos-grid">
            {items.map((item) => (
              <article className="evento-card" key={`${item.productId}-${item.size}`}>
                <div className="evento-card-contenido">
                  <h3>{item.name}</h3>
                  <p>Talla: {item.size}</p>
                  <p>Precio: {item.unitPrice.toFixed(2)} €</p>
                  <div className="tienda-controles" style={{ marginTop: 12 }}>
                    <label>Cantidad</label>
                    <input
                      type="number"
                      min="1"
                      value={item.quantity}
                      onChange={(e) =>
                        actualizarCantidad(
                          item.productId,
                          item.size,
                          parseInt(e.target.value, 10) || 0
                        )
                      }
                    />
                  </div>
                  <button
                    style={{ marginTop: 12 }}
                    onClick={() => eliminarItem(item.productId, item.size)}
                  >
                    Eliminar
                  </button>
                  {productos[item.productId]?.variants.find(
                    (v) => v.size === item.size
                  )?.stock === undefined && (
                    <p className="login-error">Producto no disponible</p>
                  )}
                </div>
              </article>
            ))}
          </div>

          <section style={{ marginTop: 32, maxWidth: 600 }}>
            <h2>Total: {total.toFixed(2)} €</h2>

            <label htmlFor="direccion">Dirección de envío</label>
            <input
              id="direccion"
              value={direccion}
              onChange={(e) => setDireccion(e.target.value)}
              placeholder="Calle, número, ciudad..."
            />

            <button
              style={{ marginTop: 16 }}
              disabled={procesando}
              onClick={() => void confirmarPedido()}
            >
              {procesando ? "Procesando..." : "Confirmar pedido"}
            </button>
          </section>
        </>
      )}
    </main>
  );
}
