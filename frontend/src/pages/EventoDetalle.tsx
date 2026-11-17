import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import {
  obtenerEvento,
  obtenerPasesDeEvento,
  crearPase,
  obtenerLineUp,
  crearActuacion,
  comprarEntrada,
  type Evento,
  type Pase,
  type Actuacion,
} from "../services/eventos";

function formatFecha(fecha: string) {
  return new Date(fecha).toLocaleDateString("es-ES");
}

export default function EventoDetalle() {
  const { id } = useParams<{ id: string }>();
  const { usuario } = useAuth();

  const [evento, setEvento] = useState<Evento | null>(null);
  const [pases, setPases] = useState<Pase[]>([]);
  const [actuaciones, setActuaciones] = useState<Actuacion[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");

  const esAdmin = usuario?.role === "admin";

  useEffect(() => {
    if (!id) return;
    Promise.all([
      obtenerEvento(id),
      obtenerPasesDeEvento(id),
      obtenerLineUp(id),
    ])
      .then(([evt, p, l]) => {
        setEvento(evt);
        setPases(p);
        setActuaciones(l);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Error al cargar el evento");
      })
      .finally(() => {
        setCargando(false);
      });
  }, [id]);

  async function recargar() {
    if (!id) return;
    setError("");
    try {
      const [evt, p, l] = await Promise.all([
        obtenerEvento(id),
        obtenerPasesDeEvento(id),
        obtenerLineUp(id),
      ]);
      setEvento(evt);
      setPases(p);
      setActuaciones(l);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar el evento");
    }
  }

  async function comprar(pase: Pase) {
    if (!usuario || !id) return;
    setMensaje("");
    setError("");
    try {
      await comprarEntrada({
        event_id: id,
        pass_id: pase.id,
        user_id: usuario.id,
      });
      setMensaje(`Entrada ${pase.type_name} comprada correctamente`);
      await recargar();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al comprar la entrada");
    }
  }

  // Formulario admin pase
  const [tipo, setTipo] = useState("");
  const [precio, setPrecio] = useState("");
  const [capacidad, setCapacidad] = useState("");
  const [beneficios, setBeneficios] = useState("");

  async function agregarPase(e: React.FormEvent) {
    e.preventDefault();
    if (!id) return;
    try {
      await crearPase(id, {
        type_name: tipo,
        price: parseFloat(precio),
        capacity: parseInt(capacidad, 10),
        benefits: beneficios.split(",").map((b) => b.trim()).filter(Boolean),
      });
      setTipo("");
      setPrecio("");
      setCapacidad("");
      setBeneficios("");
      await recargar();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear el pase");
    }
  }

  // Formulario admin line-up
  const [artistId, setArtistId] = useState("");
  const [artistName, setArtistName] = useState("");
  const [stage, setStage] = useState("");
  const [inicio, setInicio] = useState("");
  const [fin, setFin] = useState("");

  async function agregarActuacion(e: React.FormEvent) {
    e.preventDefault();
    if (!id) return;
    try {
      await crearActuacion(id, {
        artist_id: artistId,
        artist_name: artistName,
        stage,
        start_time: new Date(inicio).toISOString(),
        end_time: new Date(fin).toISOString(),
      });
      setArtistId("");
      setArtistName("");
      setStage("");
      setInicio("");
      setFin("");
      await recargar();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al añadir la actuación");
    }
  }

  if (cargando) return <p className="pagina-eventos">Cargando evento...</p>;
  if (!evento) return <p className="pagina-eventos">Evento no encontrado.</p>;

  return (
    <main className="pagina-eventos">
      <div className="eventos-encabezado">
        <p className="subtitulo">FESTIVAL</p>
        <h1>{evento.name}</h1>
        <p>
          {evento.venue} — {evento.location_city}
        </p>
        <p>
          📅 {formatFecha(evento.start_date)} — {formatFecha(evento.end_date)}
        </p>
      </div>

      {mensaje && <p className="registro-exito">{mensaje}</p>}
      {error && <p className="login-error">{error}</p>}

      <section style={{ marginBottom: 48 }}>
        <h2>Tipos de pase</h2>
        {pases.length === 0 && <p>No hay pases configurados.</p>}
        <div className="eventos-grid">
          {pases.map((pase) => (
            <article className="evento-card" key={pase.id}>
              <div className="evento-card-contenido">
                <span className="evento-etiqueta">{pase.type_name}</span>
                <h3>{pase.price.toFixed(2)} €</h3>
                <p>
                  Disponibles: {pase.available_tickets} / {pase.capacity}
                </p>
                {pase.benefits.length > 0 && (
                  <p>Beneficios: {pase.benefits.join(", ")}</p>
                )}
                {usuario?.role === "client" && pase.available_tickets > 0 && (
                  <button onClick={() => void comprar(pase)}>
                    Comprar entrada
                  </button>
                )}
                {usuario?.role === "client" && pase.available_tickets === 0 && (
                  <p>Aforo completo</p>
                )}
                {!usuario && <p><Link to="/login">Inicia sesión</Link> para comprar</p>}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section style={{ marginBottom: 48 }}>
        <h2>Line-up</h2>
        {actuaciones.length === 0 && <p>No hay actuaciones programadas.</p>}
        <div className="eventos-grid">
          {actuaciones.map((act) => (
            <article className="evento-card" key={act.id}>
              <div className="evento-card-contenido">
                <span className="evento-etiqueta">{act.stage}</span>
                <h3>{act.artist_name}</h3>
                <p>
                  {new Date(act.start_time).toLocaleString("es-ES")} —{" "}
                  {new Date(act.end_time).toLocaleString("es-ES")}
                </p>
              </div>
            </article>
          ))}
        </div>
      </section>

      {esAdmin && (
        <>
          <section style={{ marginBottom: 48 }}>
            <h2>Añadir pase</h2>
            <form className="login-formulario" onSubmit={agregarPase}>
              <label>Tipo de pase</label>
              <input value={tipo} onChange={(e) => setTipo(e.target.value)} required />

              <label>Precio (€)</label>
              <input
                type="number"
                min="0"
                step="0.01"
                value={precio}
                onChange={(e) => setPrecio(e.target.value)}
                required
              />

              <label>Capacidad</label>
              <input
                type="number"
                min="1"
                value={capacidad}
                onChange={(e) => setCapacidad(e.target.value)}
                required
              />

              <label>Beneficios (separados por comas)</label>
              <input
                value={beneficios}
                onChange={(e) => setBeneficios(e.target.value)}
              />

              <button type="submit">Crear pase</button>
            </form>
          </section>

          <section style={{ marginBottom: 48 }}>
            <h2>Añadir actuación</h2>
            <form className="login-formulario" onSubmit={agregarActuacion}>
              <label>ID del artista</label>
              <input value={artistId} onChange={(e) => setArtistId(e.target.value)} required />

              <label>Nombre del artista</label>
              <input value={artistName} onChange={(e) => setArtistName(e.target.value)} required />

              <label>Escenario</label>
              <input value={stage} onChange={(e) => setStage(e.target.value)} required />

              <label>Inicio (ISO 8601, con zona horaria)</label>
              <input
                type="datetime-local"
                value={inicio}
                onChange={(e) => setInicio(e.target.value)}
                required
              />

              <label>Fin (ISO 8601, con zona horaria)</label>
              <input
                type="datetime-local"
                value={fin}
                onChange={(e) => setFin(e.target.value)}
                required
              />

              <button type="submit">Añadir actuación</button>
            </form>
          </section>
        </>
      )}
    </main>
  );
}
