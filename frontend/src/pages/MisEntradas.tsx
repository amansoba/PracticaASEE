import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import {
  obtenerEntradasDeUsuario,
  obtenerEvento,
  type Entrada,
  type Evento,
} from "../services/eventos";

export default function MisEntradas() {
  const { usuario } = useAuth();
  const [entradas, setEntradas] = useState<Entrada[]>([]);
  const [eventos, setEventos] = useState<Record<string, Evento>>({});
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!usuario) return;

    let activo = true;

    async function cargar() {
      try {
        const datos = await obtenerEntradasDeUsuario(usuario.id);
        if (!activo) return;
        setEntradas(datos);

        const ids = Array.from(new Set(datos.map((e) => e.event_id)));
        const eventosCargados: Record<string, Evento> = {};
        await Promise.all(
          ids.map(async (id) => {
            try {
              eventosCargados[id] = await obtenerEvento(id);
            } catch {
              // ignorar
            }
          })
        );
        if (activo) setEventos(eventosCargados);
      } catch (err) {
        if (activo) {
          setError(err instanceof Error ? err.message : "No se pudieron cargar las entradas");
        }
      } finally {
        if (activo) setCargando(false);
      }
    }

    void cargar();

    return () => {
      activo = false;
    };
  }, [usuario]);

  if (!usuario) {
    return (
      <main className="pagina-eventos">
        <h1>Mis entradas</h1>
        <p>Debes iniciar sesión para ver tus entradas.</p>
        <Link to="/login" className="navbar-login">Iniciar sesión</Link>
      </main>
    );
  }

  return (
    <main className="pagina-eventos">
      <div className="eventos-encabezado">
        <p className="subtitulo">TU EXPERIENCIA SUBSONIC</p>
        <h1>Mis entradas</h1>
      </div>

      {cargando && <p>Cargando entradas...</p>}
      {error && <p className="login-error">{error}</p>}

      {!cargando && !error && entradas.length === 0 && (
        <p>Todavía no tienes entradas.</p>
      )}

      <div className="eventos-grid">
        {entradas.map((entrada) => {
          const evento = eventos[entrada.event_id];
          return (
            <article className="evento-card" key={entrada.id}>
              <div className="evento-card-contenido">
                <span className="evento-etiqueta">{entrada.status}</span>
                <h2>{evento?.name || "Evento"}</h2>
                {evento && (
                  <p>
                    {evento.location_city} —{" "}
                    {new Date(evento.start_date).toLocaleDateString("es-ES")}
                  </p>
                )}
                <p className="pedido-identificador">QR: {entrada.qr_code}</p>
                <p className="pedido-identificador">{entrada.id}</p>
              </div>
            </article>
          );
        })}
      </div>
    </main>
  );
}
