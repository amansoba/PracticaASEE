
import { useEffect, useState } from "react";
import { obtenerArtistas, type Artista } from "../services/artistas";

function Artistas() {
  const [artistas, setArtistas] = useState<Artista[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    obtenerArtistas()
      .then(setArtistas)
      .catch(() => setError("No se pudieron cargar los artistas"))
      .finally(() => setCargando(false));
  }, []);

  return (
    <main className="pagina-eventos">
      <div className="eventos-encabezado">
        <p className="subtitulo">EL SONIDO DE SUBSONIC</p>
        <h1>Artistas</h1>
        <p>Descubre los artistas de nuestro catálogo musical.</p>
      </div>

      {cargando && <p>Cargando artistas...</p>}
      {error && <p role="alert">{error}</p>}

      {!cargando && !error && artistas.length === 0 && (
        <p>No hay artistas disponibles.</p>
      )}

      <div className="eventos-grid">
        {artistas.map((artista) => (
          <article className="evento-card" key={artista.id}>
            {artista.image_url && (
              <img
                src={artista.image_url}
                alt={artista.name}
                className="artista-imagen"
              />
            )}

            <div className="evento-card-contenido">
              <span className="evento-etiqueta">{artista.genre}</span>
              <h2>{artista.name}</h2>
              <p>{artista.biography || "Biografía no disponible."}</p>
            </div>
          </article>
        ))}
      </div>
    </main>
  );
}

export default Artistas;
