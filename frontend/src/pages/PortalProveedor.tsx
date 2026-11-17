/* eslint-disable react-hooks/set-state-in-effect */
import { useEffect, useRef, useState, type FormEvent } from "react";
import { useAuth } from "../context/useAuth";
import { obtenerEventos, type Evento } from "../services/eventos";
import { obtenerMiEmpresa, type MiEmpresaProveedor, type PropuestaProveedor, ProveedorApiError } from "../services/proveedores";
import { crearPropuesta, crearProveedor, obtenerEspacios, obtenerMisPropuestas, type DatosProveedor, type Espacio } from "../services/proveedoresAdmin";

const formularioInicial: DatosProveedor = { user_id: "", company_name: "", cif_nif: "", service_category: "", contact_email: "" };

export default function PortalProveedor() {
  const { usuario, token } = useAuth();
  const [empresa, setEmpresa] = useState<MiEmpresaProveedor | null>(null);
  const [puedeRegistrar, setPuedeRegistrar] = useState(false);
  const [formulario, setFormulario] = useState(formularioInicial);
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [espacios, setEspacios] = useState<Espacio[]>([]);
  const [propuestas, setPropuestas] = useState<PropuestaProveedor[]>([]);
  const [eventoId, setEventoId] = useState("");
  const [espacioId, setEspacioId] = useState("");
  const [presupuesto, setPresupuesto] = useState(0);
  const [fechaMontaje, setFechaMontaje] = useState("");
  const [cargando, setCargando] = useState(true);
  const [cargandoEspacios, setCargandoEspacios] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const consultaEspacios = useRef(0);

  useEffect(() => {
    if (!usuario || !token || usuario.role !== "provider") return;
    setFormulario({ ...formularioInicial, user_id: usuario.id });
    void Promise.all([obtenerEventos(), obtenerMiEmpresa(token).then((dato) => ({ dato, noExiste: false })).catch((err: unknown) => {
      if (err instanceof ProveedorApiError && err.status === 404) return { dato: null, noExiste: true };
      throw err;
    })]).then(async ([datosEventos, resultadoEmpresa]) => {
      setEventos(datosEventos);
      setEmpresa(resultadoEmpresa.dato);
      setPuedeRegistrar(resultadoEmpresa.noExiste);
      if (resultadoEmpresa.dato) setPropuestas(await obtenerMisPropuestas(resultadoEmpresa.dato.id, token));
    }).catch((err: unknown) => {
      setError(err instanceof Error ? err.message : "No se pudo cargar el portal del proveedor.");
      setPuedeRegistrar(false);
    }).finally(() => setCargando(false));
  }, [usuario, token]);

  async function registrarEmpresa(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (!token || !formulario.company_name.trim() || !formulario.cif_nif.trim() || !formulario.service_category.trim() || !formulario.contact_email.includes("@")) {
      setError("Completa todos los campos y utiliza un email válido.");
      return;
    }
    try {
      const creada = await crearProveedor(formulario, token);
      setEmpresa(creada);
      setPuedeRegistrar(false);
      setMensaje("Empresa registrada correctamente.");
      setPropuestas([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo registrar la empresa.");
    }
  }

  async function seleccionarEvento(id: string) {
    const consultaActual = ++consultaEspacios.current;
    setEventoId(id);
    setEspacioId("");
    setEspacios([]);
    if (!id) return;
    setCargandoEspacios(true);
    setError("");
    try {
      const datos = await obtenerEspacios(id);
      if (consultaActual === consultaEspacios.current) setEspacios(datos);
    } catch (err) {
      if (consultaActual === consultaEspacios.current) setError(err instanceof Error ? err.message : "No se pudieron cargar los espacios.");
    } finally {
      if (consultaActual === consultaEspacios.current) setCargandoEspacios(false);
    }
  }

  async function enviarPropuesta(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (!token || !empresa || !eventoId || !espacioId || presupuesto <= 0) {
      setError("Selecciona evento y espacio e introduce un presupuesto positivo.");
      return;
    }
    try {
      await crearPropuesta({ event_id: eventoId, space_id: espacioId, provider_id: empresa.id, budget_proposal: presupuesto, setup_date: fechaMontaje || undefined }, token);
      setMensaje("Propuesta enviada correctamente.");
      setPropuestas(await obtenerMisPropuestas(empresa.id, token));
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo enviar la propuesta.");
    }
  }

  if (!usuario || usuario.role !== "provider" || !token) return <main className="pagina-eventos"><h1>Portal del proveedor</h1><p role="alert">Esta sección está reservada a proveedores.</p></main>;
  if (cargando) return <main className="pagina-eventos"><p role="status">Cargando portal...</p></main>;
  if (error && !empresa && !puedeRegistrar) return <main className="pagina-eventos"><h1>Portal del proveedor</h1><p role="alert">{error}</p></main>;

  return <main className="pagina-eventos"><div className="eventos-encabezado"><p className="subtitulo">PORTAL DEL PROVEEDOR</p><h1>{empresa ? empresa.company_name : "Registrar empresa"}</h1><p>Gestiona tu empresa, espacios y propuestas.</p></div>{mensaje && <p role="status">{mensaje}</p>}{error && <p role="alert">{error}</p>}{!empresa && puedeRegistrar ? <section className="admin-seccion"><h2>Datos de la empresa</h2><form className="admin-form" onSubmit={(event) => void registrarEmpresa(event)}>{(["company_name", "cif_nif", "service_category", "contact_email"] as const).map((campo) => <label key={campo}>{campo}<input required type={campo === "contact_email" ? "email" : "text"} value={formulario[campo]} onChange={(event) => setFormulario({ ...formulario, [campo]: event.target.value })} /></label>)}<button type="submit">Registrar empresa</button></form></section> : empresa && <><section className="admin-seccion"><h2>Nueva propuesta</h2><form className="admin-form" onSubmit={(event) => void enviarPropuesta(event)}><label>Evento<select required value={eventoId} onChange={(event) => void seleccionarEvento(event.target.value)}><option value="">Selecciona un evento</option>{eventos.map((evento) => <option key={evento.id} value={evento.id}>{evento.name}</option>)}</select></label><label>Espacio<select required value={espacioId} disabled={!eventoId || cargandoEspacios} onChange={(event) => setEspacioId(event.target.value)}><option value="">{cargandoEspacios ? "Cargando..." : "Selecciona un espacio"}</option>{espacios.filter((espacio) => espacio.is_available).map((espacio) => <option key={espacio.id} value={espacio.id}>{espacio.name}</option>)}</select></label><label>Presupuesto<input required min="0.01" step="0.01" type="number" value={presupuesto} onChange={(event) => setPresupuesto(Number(event.target.value))} /></label><label>Fecha de montaje<input type="date" value={fechaMontaje} onChange={(event) => setFechaMontaje(event.target.value)} /></label><button type="submit">Enviar propuesta</button></form></section><section className="admin-seccion"><h2>Mis propuestas</h2>{propuestas.length === 0 ? <p>No tienes propuestas registradas.</p> : <ul>{propuestas.map((propuesta) => <li key={propuesta.id}>Evento {propuesta.event_id} · Espacio {propuesta.space_id} · {propuesta.budget_proposal.toFixed(2)} € · {propuesta.status}</li>)}</ul>}</section></>}</main>;
}
