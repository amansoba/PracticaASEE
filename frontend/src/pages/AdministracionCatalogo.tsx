/* eslint-disable react-hooks/set-state-in-effect, react-hooks/exhaustive-deps */
import { useEffect, useState, type FormEvent } from "react";
import { useAuth } from "../context/useAuth";
import {
  actualizarArtista, crearArtista, eliminarArtista, obtenerArtistas,
  type Artista, type DatosArtista,
} from "../services/artistas";
import {
  crearCancion, obtenerCanciones, type Cancion, type DatosCancion,
} from "../services/catalogoAdmin";

const artistaInicial: DatosArtista = { name: "", genre: "", biography: "", image_url: "" };
const cancionInicial: DatosCancion = { title: "", spotify_id: "", spotify_url: "", preview_url: "" };

function esUrlValida(valor: string): boolean {
  return !valor.trim() || URL.canParse(valor.trim());
}

export default function AdministracionCatalogo() {
  const { usuario, token } = useAuth();
  const [artistas, setArtistas] = useState<Artista[]>([]);
  const [busqueda, setBusqueda] = useState("");
  const [genero, setGenero] = useState("");
  const [artistaForm, setArtistaForm] = useState<DatosArtista>(artistaInicial);
  const [artistaEditado, setArtistaEditado] = useState<string | null>(null);
  const [artistaCanciones, setArtistaCanciones] = useState<string | null>(null);
  const [canciones, setCanciones] = useState<Cancion[]>([]);
  const [cancionForm, setCancionForm] = useState<DatosCancion>(cancionInicial);
  const [cargando, setCargando] = useState(true);
  const [cargandoCanciones, setCargandoCanciones] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  async function cargarArtistas() {
    setCargando(true);
    try {
      const datos = await obtenerArtistas({ search: busqueda, genre: genero });
      setArtistas(datos);
      setError("");
      if (artistaCanciones && !datos.some((artista) => artista.id === artistaCanciones)) {
        setArtistaCanciones(null);
        setCanciones([]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudieron cargar los artistas");
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    void cargarArtistas();
  }, [busqueda, genero]);

  function limpiarMensajes() {
    setError("");
    setMensaje("");
  }

  async function guardarArtista(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    limpiarMensajes();
    if (!token || !artistaForm.name?.trim() || !artistaForm.genre?.trim()) {
      setError("El nombre y el género del artista son obligatorios.");
      return;
    }
    if (!esUrlValida(artistaForm.image_url ?? "")) {
      setError("La URL de imagen del artista no es válida.");
      return;
    }
    setGuardando(true);
    try {
      if (artistaEditado) {
        await actualizarArtista(artistaEditado, artistaForm, token);
        setMensaje("Artista actualizado correctamente.");
      } else {
        await crearArtista(artistaForm, token);
        setMensaje("Artista creado correctamente.");
      }
      setArtistaForm(artistaInicial);
      setArtistaEditado(null);
      await cargarArtistas();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo guardar el artista.");
    } finally {
      setGuardando(false);
    }
  }

  async function borrarArtista(id: string) {
    if (!token || !window.confirm("¿Seguro que quieres eliminar este artista?")) return;
    limpiarMensajes();
    try {
      await eliminarArtista(id, token);
      if (artistaCanciones === id) {
        setArtistaCanciones(null);
        setCanciones([]);
      }
      setMensaje("Artista eliminado correctamente.");
      await cargarArtistas();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo eliminar el artista.");
    }
  }

  async function cargarCanciones(artistId: string) {
    setArtistaCanciones(artistId);
    setCargandoCanciones(true);
    setError("");
    try {
      setCanciones(await obtenerCanciones(artistId));
    } catch (err) {
      setCanciones([]);
      setError(err instanceof Error ? err.message : "No se pudieron cargar las canciones.");
    } finally {
      setCargandoCanciones(false);
    }
  }

  async function guardarCancion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    limpiarMensajes();
    if (!token || !artistaCanciones || !cancionForm.title.trim()) {
      setError("Selecciona un artista e introduce el título de la canción.");
      return;
    }
    if (!esUrlValida(cancionForm.spotify_url ?? "") || !esUrlValida(cancionForm.preview_url ?? "")) {
      setError("Las URLs de Spotify y de preescucha deben ser válidas.");
      return;
    }
    setGuardando(true);
    try {
      const datos: DatosCancion = {
        title: cancionForm.title.trim(),
        ...(cancionForm.spotify_id?.trim() ? { spotify_id: cancionForm.spotify_id.trim() } : {}),
        ...(cancionForm.spotify_url?.trim() ? { spotify_url: cancionForm.spotify_url.trim() } : {}),
        ...(cancionForm.preview_url?.trim() ? { preview_url: cancionForm.preview_url.trim() } : {}),
      };
      await crearCancion(artistaCanciones, datos, token);
      setCancionForm(cancionInicial);
      setMensaje("Canción creada correctamente.");
      await cargarCanciones(artistaCanciones);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo crear la canción.");
    } finally {
      setGuardando(false);
    }
  }

  if (!usuario || usuario.role !== "admin" || !token) {
    return <main className="pagina-eventos"><h1>Administración de catálogo</h1><p role="alert">Se requieren permisos de administrador.</p></main>;
  }

  return (
    <main className="pagina-eventos">
      <div className="eventos-encabezado"><p className="subtitulo">ADMINISTRACIÓN</p><h1>Catálogo musical</h1><p>Gestiona artistas y canciones conforme al contrato del catálogo.</p></div>
      {mensaje && <p role="status">{mensaje}</p>}
      {error && <p role="alert">{error}</p>}
      <section className="admin-seccion">
        <h2>{artistaEditado ? "Editar artista" : "Nuevo artista"}</h2>
        <form className="admin-form" onSubmit={(event) => void guardarArtista(event)}>
          <label>Nombre<input required value={artistaForm.name} onChange={(event) => setArtistaForm({ ...artistaForm, name: event.target.value })} /></label>
          <label>Género<input required value={artistaForm.genre} onChange={(event) => setArtistaForm({ ...artistaForm, genre: event.target.value })} /></label>
          <label>Biografía<input value={artistaForm.biography ?? ""} onChange={(event) => setArtistaForm({ ...artistaForm, biography: event.target.value })} /></label>
          <label>URL de imagen<input type="url" value={artistaForm.image_url ?? ""} onChange={(event) => setArtistaForm({ ...artistaForm, image_url: event.target.value })} /></label>
          <button type="submit" disabled={guardando}>{guardando ? "Guardando..." : artistaEditado ? "Guardar cambios" : "Crear artista"}</button>
          {artistaEditado && <button type="button" onClick={() => { setArtistaEditado(null); setArtistaForm(artistaInicial); }}>Cancelar</button>}
        </form>
      </section>
      <section className="admin-seccion">
        <h2>Artistas</h2>
        <div className="admin-filtros"><label>Buscar por nombre<input value={busqueda} onChange={(event) => setBusqueda(event.target.value)} /></label><label>Filtrar por género<input value={genero} onChange={(event) => setGenero(event.target.value)} /></label></div>
        {cargando ? <p role="status">Cargando artistas...</p> : artistas.length === 0 ? <p>No hay artistas que coincidan con los filtros.</p> : <div className="admin-tabla">{artistas.map((artista) => <article className="evento-card" key={artista.id}><div className="evento-card-contenido"><h3>{artista.name}</h3><p>{artista.genre}</p><button type="button" onClick={() => { setArtistaEditado(artista.id); setArtistaForm({ name: artista.name, genre: artista.genre, biography: artista.biography, image_url: artista.image_url }); }}>Editar</button>{" "}<button type="button" onClick={() => void borrarArtista(artista.id)}>Eliminar</button>{" "}<button type="button" onClick={() => void cargarCanciones(artista.id)}>Canciones</button></div></article>)}</div>}
      </section>
      {artistaCanciones && <section className="admin-seccion"><h2>Canciones</h2><form className="admin-form" onSubmit={(event) => void guardarCancion(event)}><label>Título<input required value={cancionForm.title} onChange={(event) => setCancionForm({ ...cancionForm, title: event.target.value })} /></label><label>Spotify ID<input value={cancionForm.spotify_id ?? ""} onChange={(event) => setCancionForm({ ...cancionForm, spotify_id: event.target.value })} /></label><label>Spotify URL<input type="url" value={cancionForm.spotify_url ?? ""} onChange={(event) => setCancionForm({ ...cancionForm, spotify_url: event.target.value })} /></label><label>Preview URL<input type="url" value={cancionForm.preview_url ?? ""} onChange={(event) => setCancionForm({ ...cancionForm, preview_url: event.target.value })} /></label><button type="submit" disabled={guardando}>{guardando ? "Guardando..." : "Añadir canción"}</button></form>{cargandoCanciones ? <p role="status">Cargando canciones...</p> : canciones.length === 0 ? <p>No hay canciones para este artista.</p> : <ul>{canciones.map((cancion) => <li key={cancion.id}>{cancion.title}{cancion.spotify_url && <> · <a href={cancion.spotify_url}>Spotify</a></>}</li>)}</ul>}<small>El contrato actual no permite editar ni eliminar canciones.</small></section>}
    </main>
  );
}
