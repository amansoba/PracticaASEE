
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  obtenerProductos,
  crearPedido,
  type Producto,
} from "../services/tienda";
import { useAuth } from "../context/useAuth";

function Tienda() {
  const navigate = useNavigate();
  const { usuario, token } = useAuth();

  const [productos, setProductos] = useState<Producto[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [tallas, setTallas] = useState<Record<string, string>>({});
  const [cantidades, setCantidades] = useState<Record<string, number>>({});
  const [direcciones, setDirecciones] = useState<Record<string, string>>({});
  const [procesando, setProcesando] = useState<string | null>(null);
  const [mensajes, setMensajes] = useState<Record<string, string>>({});

  async function cargarProductos() {
    try {
      const datos = await obtenerProductos();
      setProductos(datos);
    } catch {
      setError("No se pudieron cargar los productos");
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    void cargarProductos();
  }, []);

  async function confirmarCompra(producto: Producto) {
    if (!usuario || !token) {
      navigate("/login");
      return;
    }

    const talla = tallas[producto.id];
    const cantidad = cantidades[producto.id] ?? 1;
    const direccion = direcciones[producto.id]?.trim();

    if (!talla || !direccion) {
      setMensajes({
        ...mensajes,
        [producto.id]: "Selecciona una talla e introduce tu dirección.",
      });
      return;
    }

    const variante = producto.variants.find(
      (item) => item.size === talla
    );

    if (!variante || cantidad > variante.stock) {
      setMensajes({
        ...mensajes,
        [producto.id]: "No hay stock suficiente.",
      });
      return;
    }

    setProcesando(producto.id);
    setMensajes({ ...mensajes, [producto.id]: "" });

    try {
      const pedido = await crearPedido(
        {
          user_id: usuario.id,
          shipping_address: direccion,
          items: [
            {
              product_id: producto.id,
              size: talla,
              quantity: cantidad,
              unit_price: producto.price,
            },
          ],
        },
        token
      );

      setMensajes((anteriores) => ({
        ...anteriores,
        [producto.id]: `Pedido ${pedido.id} registrado. Total: ${pedido.total_price.toFixed(2)} €`,
      }));

      setCantidades((anteriores) => ({
        ...anteriores,
        [producto.id]: 1,
      }));

      await cargarProductos();
    } catch (err) {
      setMensajes((anteriores) => ({
        ...anteriores,
        [producto.id]:
          err instanceof Error ? err.message : "Error al realizar la compra",
      }));
    } finally {
      setProcesando(null);
    }
  }

  return (
    <main className="pagina-eventos">
      <div className="eventos-encabezado">
        <p className="subtitulo">MERCHANDISING OFICIAL</p>
        <h1>Tienda Subsonic</h1>
        <p>Selecciona tu producto y realiza tu pedido.</p>
      </div>

      {cargando && <p>Cargando productos...</p>}
      {error && <p role="alert">{error}</p>}

      {!cargando && !error && productos.length === 0 && (
        <p>No hay productos disponibles.</p>
      )}

      <div className="eventos-grid">
        {productos.map((producto) => {
          const talla = tallas[producto.id] ?? "";
          const cantidad = cantidades[producto.id] ?? 1;
          const variante = producto.variants.find(
            (item) => item.size === talla
          );
          const stock = variante?.stock ?? 0;
          const comprando = procesando === producto.id;

          return (
            <article className="evento-card" key={producto.id}>
              <div className="evento-card-contenido">
                <span className="evento-etiqueta">{producto.category}</span>
                <h2>{producto.name}</h2>
                <p>{producto.description}</p>
                <h3>{producto.price.toFixed(2)} €</h3>

                <div className="tienda-controles">
                  <label htmlFor={`talla-${producto.id}`}>Talla</label>
                  <select
                    id={`talla-${producto.id}`}
                    value={talla}
                    onChange={(e) => {
                      setTallas((anteriores) => ({
                        ...anteriores,
                        [producto.id]: e.target.value,
                      }));
                      setCantidades((anteriores) => ({
                        ...anteriores,
                        [producto.id]: 1,
                      }));
                    }}
                  >
                    <option value="">Selecciona una talla</option>
                    {producto.variants.map((item) => (
                      <option
                        key={item.size}
                        value={item.size}
                        disabled={item.stock === 0}
                      >
                        {item.size} — {item.stock} disponibles
                      </option>
                    ))}
                  </select>

                  <label htmlFor={`cantidad-${producto.id}`}>Cantidad</label>
                  <input
                    id={`cantidad-${producto.id}`}
                    type="number"
                    min="1"
                    max={stock || 1}
                    value={cantidad}
                    disabled={!variante || stock === 0}
                    onChange={(e) => {
                      const valor = Number(e.target.value);
                      setCantidades((anteriores) => ({
                        ...anteriores,
                        [producto.id]: Math.min(
                          Math.max(valor || 1, 1),
                          stock
                        ),
                      }));
                    }}
                  />

                  <label htmlFor={`direccion-${producto.id}`}>
                    Dirección de envío
                  </label>
                  <input
                    id={`direccion-${producto.id}`}
                    type="text"
                    placeholder="Calle, número, ciudad..."
                    value={direcciones[producto.id] ?? ""}
                    onChange={(e) =>
                      setDirecciones((anteriores) => ({
                        ...anteriores,
                        [producto.id]: e.target.value,
                      }))
                    }
                  />

                  <p>
                    Total: <strong>{(producto.price * cantidad).toFixed(2)} €</strong>
                  </p>

                  <button
                    type="button"
                    disabled={!variante || cantidad > stock || comprando}
                    onClick={() => void confirmarCompra(producto)}
                  >
                    {comprando ? "Procesando..." : "Confirmar compra"}
                  </button>

                  {mensajes[producto.id] && (
                    <p role="status">{mensajes[producto.id]}</p>
                  )}
                </div>
              </div>
            </article>
          );
        })}
      </div>
    </main>
  );
}

export default Tienda;
