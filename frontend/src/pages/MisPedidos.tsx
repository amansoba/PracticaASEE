
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { obtenerPedidosUsuario, type Pedido } from "../services/tienda";

function MisPedidos() {
  const { usuario, token } = useAuth();
  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

    useEffect(() => {
    if (!usuario || !token) {
      return;
    }

    let activo = true;

    obtenerPedidosUsuario(usuario.id, token)
      .then((datos) => {
        if (activo) setPedidos(datos);
      })
      .catch((err) => {
        if (activo) {
          setError(
            err instanceof Error
              ? err.message
              : "No se pudieron cargar los pedidos"
          );
        }
      })
      .finally(() => {
        if (activo) setCargando(false);
      });

    return () => {
      activo = false;
    };
  }, [usuario, token]);

  if (!usuario || !token) {
    return (
      <main className="pagina-eventos">
        <h1>Mis pedidos</h1>
        <p>Debes iniciar sesión para consultar tus compras.</p>
        <Link to="/login" className="navbar-login">
          Iniciar sesión
        </Link>
      </main>
    );
  }

  return (
    <main className="pagina-eventos">
      <div className="eventos-encabezado">
        <p className="subtitulo">TU EXPERIENCIA SUBSONIC</p>
        <h1>Mis pedidos</h1>
        <p>Consulta el historial de tus compras.</p>
      </div>

      {cargando && <p>Cargando pedidos...</p>}
      {error && <p role="alert">{error}</p>}

      {!cargando && !error && pedidos.length === 0 && (
        <p>Todavía no has realizado ningún pedido.</p>
      )}

      <div className="eventos-grid">
        {pedidos.map((pedido) => (
          <article className="evento-card" key={pedido.id}>
            <div className="evento-card-contenido">
              <span className="evento-etiqueta">
                {pedido.status}
              </span>

              <h2>Pedido</h2>
              <p className="pedido-identificador">{pedido.id}</p>

              <p>
                Fecha: {new Date(pedido.created_at).toLocaleString("es-ES")}
              </p>

              <h3>Artículos</h3>

              {pedido.items.map((item, indice) => (
                <div
                  className="pedido-articulo"
                  key={`${pedido.id}-${indice}`}
                >
                  <p>Producto: {item.product_id}</p>
                  <p>Talla: {item.size}</p>
                  <p>Cantidad: {item.quantity}</p>
                  <p>Precio unitario: {item.unit_price.toFixed(2)} €</p>
                </div>
              ))}

              <h3>Total: {pedido.total_price.toFixed(2)} €</h3>
            </div>
          </article>
        ))}
      </div>
    </main>
  );
}

export default MisPedidos;
