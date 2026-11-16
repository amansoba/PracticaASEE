import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { obtenerEventos, type Evento } from "../services/eventos";

function Eventos() {
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    obtenerEventos()
      .then(setEventos)
      .catch(() => setError("No se pudieron cargar los eventos"))
      .finally(() => setCargando(false));
  }, []);

  return (
    <main className="pagina-eventos">
      <div className="eventos-encabezado">
        <p className="subtitulo">DESCUBRE SUBSONIC</p>
        <h1>Festivales y eventos</h1>
        <p>Explora las próximas experiencias musicales.</p>
      </div>

      {cargando && <p>Cargando eventos...</p>}
      {error && <p role="alert">{error}</p>}

      {!cargando && !error && eventos.length === 0 && (
        <p>No hay eventos disponibles.</p>
      )}

      <div className="eventos-grid">
        {eventos.map((evento) => (
          <Link
            to={`/eventos/${evento.id}`}
            className="evento-card"
            key={evento.id}
          >
            <div className="evento-card-contenido">
              <span className="evento-etiqueta">FESTIVAL</span>

              <h2>{evento.name}</h2>

              <p>📍 {evento.location_city}</p>
              <p>🏟️ {evento.venue}</p>
              <p>📅 {evento.start_date} — {evento.end_date}</p>
            </div>
          </Link>
        ))}
      </div>
    </main>
  );
}

export default Eventos;
