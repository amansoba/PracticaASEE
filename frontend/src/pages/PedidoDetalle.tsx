import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import {
  obtenerPedido,
  actualizarEstadoPedido,
  type Pedido,
} from "../services/tienda";

export default function PedidoDetalle() {
  const { id } = useParams<{ id: string }>();
  const { usuario } = useAuth();
  const [pedido, setPedido] = useState<Pedido | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");

  useEffect(() => {
    if (!id) return;
    obtenerPedido(id)
      .then(setPedido)
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Error al cargar el pedido");
      })
      .finally(() => {
        setCargando(false);
      });
  }, [id]);

  async function cancelar() {
    if (!id) return;
    setError("");
    try {
      await actualizarEstadoPedido(id, "cancelled");
      setMensaje("Pedido cancelado");
      const datos = await obtenerPedido(id);
      setPedido(datos);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo cancelar el pedido");
    }
  }

  if (!usuario) {
    return (
      <main className="pagina-eventos">
        <h1>Pedido</h1>
        <p>Debes iniciar sesión.</p>
        <Link to="/login" className="navbar-login">Iniciar sesión</Link>
      </main>
    );
  }

  if (cargando) return <main className="pagina-eventos"><p>Cargando pedido...</p></main>;
  if (!pedido) return <main className="pagina-eventos"><p>Pedido no encontrado.</p></main>;

  return (
    <main className="pagina-eventos">
      <div className="eventos-encabezado">
        <p className="subtitulo">TU COMPRA</p>
        <h1>Pedido {pedido.id}</h1>
      </div>

      {mensaje && <p className="registro-exito">{mensaje}</p>}
      {error && <p className="login-error">{error}</p>}

      <article className="evento-card" style={{ maxWidth: 700 }}>
        <div className="evento-card-contenido">
          <span className="evento-etiqueta">{pedido.status}</span>
          <p>Fecha: {new Date(pedido.created_at).toLocaleString("es-ES")}</p>

          <h3>Artículos</h3>
          {pedido.items.map((item, i) => (
            <div className="pedido-articulo" key={`${pedido.id}-${i}`}>
              <p>Producto: {item.product_id}</p>
              <p>Talla: {item.size}</p>
              <p>Cantidad: {item.quantity}</p>
              <p>Precio unitario: {item.unit_price.toFixed(2)} €</p>
            </div>
          ))}

          <h3>Total: {pedido.total_price.toFixed(2)} €</h3>

          {pedido.status === "pending" && (
            <button style={{ marginTop: 16 }} onClick={() => void cancelar()}>
              Cancelar pedido
            </button>
          )}
        </div>
      </article>
    </main>
  );
}
