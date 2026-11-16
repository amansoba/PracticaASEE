import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import {
  obtenerEventos,
  crearEvento,
  actualizarEvento,
  eliminarEvento,
  type Evento,
  type DatosEvento,
} from "../services/eventos";

export default function AdminEventos() {
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const [editando, setEditando] = useState<Evento | null>(null);
  const [nombre, setNombre] = useState("");
  const [ciudad, setCiudad] = useState("");
  const [recinto, setRecinto] = useState("");
  const [inicio, setInicio] = useState("");
  const [fin, setFin] = useState("");

  useEffect(() => {
    if (usuario?.role !== "admin") return;
    obtenerEventos()
      .then(setEventos)
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Error al cargar eventos");
      })
      .finally(() => {
        setCargando(false);
      });
  }, [usuario]);

  function resetForm() {
    setEditando(null);
    setNombre("");
    setCiudad("");
    setRecinto("");
    setInicio("");
    setFin("");
  }

  function prepararEditar(evento: Evento) {
    setEditando(evento);
    setNombre(evento.name);
    setCiudad(evento.location_city);
    setRecinto(evento.venue);
    setInicio(evento.start_date);
    setFin(evento.end_date);
  }

  function obtenerDatos(): DatosEvento {
    return {
      name: nombre.trim(),
      location_city: ciudad.trim(),
      venue: recinto.trim(),
      start_date: inicio,
      end_date: fin,
    };
  }

  async function recargarEventos() {
    const datos = await obtenerEventos();
    setEventos(datos);
  }

  async function guardar(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const datos = obtenerDatos();
      if (editando) {
        await actualizarEvento(editando.id, datos);
      } else {
        await crearEvento(datos);
      }
      resetForm();
      await recargarEventos();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al guardar el evento");
    }
  }

  async function borrar(id: string) {
    if (!confirm("¿Eliminar este evento?")) return;
    setError("");
    try {
      await eliminarEvento(id);
      await recargarEventos();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al eliminar el evento");
    }
  }

  if (!usuario || usuario.role !== "admin") {
    return (
      <main className="pagina-eventos">
        <h1>Administración</h1>
        <p>Esta sección es solo para administradores.</p>
      </main>
    );
  }

  return (
    <main className="pagina-eventos">
      <div className="eventos-encabezado">
        <p className="subtitulo">ADMINISTRACIÓN</p>
        <h1>Gestión de eventos</h1>
      </div>

      {error && <p className="login-error">{error}</p>}

      <section style={{ marginBottom: 48 }}>
        <h2>{editando ? "Editar evento" : "Crear evento"}</h2>
        <form className="login-formulario" onSubmit={guardar}>
          <label>Nombre</label>
          <input value={nombre} onChange={(e) => setNombre(e.target.value)} required />

          <label>Ciudad</label>
          <input value={ciudad} onChange={(e) => setCiudad(e.target.value)} required />

          <label>Recinto</label>
          <input value={recinto} onChange={(e) => setRecinto(e.target.value)} required />

          <label>Fecha de inicio</label>
          <input
            type="date"
            value={inicio}
            onChange={(e) => setInicio(e.target.value)}
            required
          />

          <label>Fecha de fin</label>
          <input
            type="date"
            value={fin}
            onChange={(e) => setFin(e.target.value)}
            required
          />

          <button type="submit">{editando ? "Actualizar" : "Crear"}</button>
          {editando && (
            <button type="button" onClick={resetForm} style={{ marginTop: 12, background: "#444" }}>
              Cancelar edición
            </button>
          )}
        </form>
      </section>

      <section>
        <h2>Eventos</h2>
        {cargando && <p>Cargando...</p>}
        {!cargando && eventos.length === 0 && <p>No hay eventos.</p>}

        <div className="eventos-grid">
          {eventos.map((evento) => (
            <article className="evento-card" key={evento.id}>
              <div className="evento-card-contenido">
                <h3>{evento.name}</h3>
                <p>
                  {evento.venue}, {evento.location_city}
                </p>
                <p>
                  {evento.start_date} — {evento.end_date}
                </p>
                <div style={{ display: "flex", gap: 12, marginTop: 16 }}>
                  <button onClick={() => navigate(`/eventos/${evento.id}`)}>
                    Ver / gestionar
                  </button>
                  <button onClick={() => prepararEditar(evento)}>Editar</button>
                  <button onClick={() => void borrar(evento.id)}>Eliminar</button>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
