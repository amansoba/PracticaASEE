import { useEffect, useRef, useState, type FormEvent } from "react";
import { useAuth } from "../context/useAuth";
import { obtenerEventos, type Evento } from "../services/eventos";
import { obtenerProveedores, type Proveedor } from "../services/proveedores";
import { actualizarEstadoPropuesta, crearEspacio, crearServicio, obtenerEspacios, obtenerProveedor, obtenerPropuestasEvento, obtenerServicios, type Espacio, type PropuestaProveedor, type ServicioExterno } from "../services/proveedoresAdmin";

export default function AdministracionProveedores() {
  const { usuario, token } = useAuth();
  const [proveedores, setProveedores] = useState<Proveedor[]>([]);
  const [detalle, setDetalle] = useState<Proveedor | null>(null);
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [servicios, setServicios] = useState<ServicioExterno[]>([]);
  const [espacios, setEspacios] = useState<Espacio[]>([]);
  const [propuestas, setPropuestas] = useState<PropuestaProveedor[]>([]);
  const [eventoId, setEventoId] = useState("");
  const [servicio, setServicio] = useState({ name: "", description: "" });
  const [espacio, setEspacio] = useState({ name: "", dimensions: "", base_price: 0, is_available: true });
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const consultaEvento = useRef(0);

  useEffect(() => {
    if (!token || usuario?.role !== "admin") return;
    void Promise.all([obtenerProveedores(token), obtenerEventos(), obtenerServicios()]).then(([datosProveedores, datosEventos, datosServicios]) => {
      setProveedores(datosProveedores);
      setEventos(datosEventos);
      setServicios(datosServicios);
    }).catch((err: unknown) => setError(err instanceof Error ? err.message : "No se pudieron cargar los datos."));
  }, [token, usuario]);

  async function seleccionarEvento(id: string) {
    const consultaActual = ++consultaEvento.current;
    setEventoId(id);
    setEspacios([]);
    setPropuestas([]);
    setError("");
    if (!id || !token) return;
    try {
      const [datosEspacios, datosPropuestas] = await Promise.all([obtenerEspacios(id), obtenerPropuestasEvento(id, token)]);
      if (consultaActual === consultaEvento.current) {
        setEspacios(datosEspacios);
        setPropuestas(datosPropuestas);
      }
    } catch (err) {
      if (consultaActual === consultaEvento.current) setError(err instanceof Error ? err.message : "No se pudo cargar el evento.");
    }
  }

  async function verDetalle(id: string) {
    if (!token) return;
    try { setDetalle(await obtenerProveedor(id, token)); setError(""); } catch (err) { setError(err instanceof Error ? err.message : "No se pudo cargar el proveedor."); }
  }

  async function guardarServicio(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !servicio.name.trim()) { setError("El nombre del servicio es obligatorio."); return; }
    try { const creado = await crearServicio(servicio, token); setServicios((actuales) => [...actuales, creado]); setServicio({ name: "", description: "" }); setMensaje("Servicio creado correctamente."); } catch (err) { setError(err instanceof Error ? err.message : "No se pudo crear el servicio."); }
  }

  async function guardarEspacio(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !eventoId || !espacio.name.trim() || espacio.base_price < 0) { setError("Selecciona un evento e introduce un espacio y precio válidos."); return; }
    try { const creado = await crearEspacio({ ...espacio, event_id: eventoId }, token); setEspacios((actuales) => [...actuales, creado]); setMensaje("Espacio creado correctamente."); } catch (err) { setError(err instanceof Error ? err.message : "No se pudo crear el espacio."); }
  }

  async function resolver(id: string, status: "approved" | "rejected") {
    if (!token || !window.confirm(`¿${status === "approved" ? "Aprobar" : "Rechazar"} propuesta?`)) return;
    try { await actualizarEstadoPropuesta(id, status, token); await seleccionarEvento(eventoId); setMensaje("Propuesta actualizada correctamente."); } catch (err) { setError(err instanceof Error ? err.message : "No se pudo actualizar la propuesta."); }
  }

  if (!usuario || usuario.role !== "admin" || !token) return <main className="pagina-eventos"><h1>Administración de proveedores</h1><p role="alert">Se requieren permisos de administrador.</p></main>;
  return <main className="pagina-eventos"><div className="eventos-encabezado"><p className="subtitulo">ADMINISTRACIÓN</p><h1>Proveedores y propuestas</h1><p>Empresas registradas, servicios, espacios y resoluciones.</p></div>{mensaje && <p role="status">{mensaje}</p>}{error && <p role="alert">{error}</p>}
    <section className="admin-seccion"><h2>Proveedores</h2>{proveedores.length === 0 ? <p>No hay proveedores.</p> : <ul>{proveedores.map((proveedor) => <li key={proveedor.id}>{proveedor.company_name} · {proveedor.service_category} · {proveedor.contact_email} <button type="button" onClick={() => void verDetalle(proveedor.id)}>Ver detalle</button></li>)}</ul>}{detalle && <div><h3>{detalle.company_name}</h3><p>{detalle.cif_nif} · {detalle.contact_email}</p></div>}</section>
    <section className="admin-seccion"><h2>Servicios externos</h2><form className="admin-form" onSubmit={(event) => void guardarServicio(event)}><input required placeholder="Nombre" value={servicio.name} onChange={(event) => setServicio({ ...servicio, name: event.target.value })} /><input placeholder="Descripción" value={servicio.description} onChange={(event) => setServicio({ ...servicio, description: event.target.value })} /><button type="submit">Crear servicio</button></form><ul>{servicios.map((servicioItem) => <li key={servicioItem.id}>{servicioItem.name}: {servicioItem.description}</li>)}</ul><small>El contrato no ofrece edición ni eliminación.</small></section>
    <section className="admin-seccion"><label>Evento<select value={eventoId} onChange={(event) => void seleccionarEvento(event.target.value)}><option value="">Selecciona un evento</option>{eventos.map((evento) => <option key={evento.id} value={evento.id}>{evento.name}</option>)}</select></label><h2>Espacios</h2><form className="admin-form" onSubmit={(event) => void guardarEspacio(event)}><input required placeholder="Nombre" value={espacio.name} onChange={(event) => setEspacio({ ...espacio, name: event.target.value })} /><input placeholder="Dimensiones" value={espacio.dimensions} onChange={(event) => setEspacio({ ...espacio, dimensions: event.target.value })} /><input required min="0" step="0.01" type="number" placeholder="Precio base" value={espacio.base_price} onChange={(event) => setEspacio({ ...espacio, base_price: Number(event.target.value) })} /><button type="submit">Crear espacio</button></form><ul>{espacios.map((espacioItem) => <li key={espacioItem.id}>{espacioItem.name} · {espacioItem.base_price.toFixed(2)} € · {espacioItem.is_available ? "Disponible" : "No disponible"}</li>)}</ul><small>El contrato no ofrece edición ni eliminación.</small><h2>Propuestas</h2>{propuestas.length === 0 ? <p>No hay propuestas.</p> : <ul>{propuestas.map((propuesta) => <li key={propuesta.id}>{propuesta.provider_id} · {propuesta.space_id} · {propuesta.budget_proposal.toFixed(2)} € · {propuesta.status} {propuesta.status === "pending" && <><button type="button" onClick={() => void resolver(propuesta.id, "approved")}>Aprobar</button><button type="button" onClick={() => void resolver(propuesta.id, "rejected")}>Rechazar</button></>}</li>)}</ul>}</section>
  </main>;
}
