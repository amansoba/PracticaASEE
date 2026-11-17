import { useEffect, useRef, useState, type FormEvent } from "react";
import { useAuth } from "../context/useAuth";
import { obtenerEventos, type Evento } from "../services/eventos";
import { obtenerProveedores, type Proveedor } from "../services/proveedores";

import {
  actualizarEspacio,
  actualizarServicio,
  actualizarEstadoPropuesta,
  crearEspacio,
  crearServicio,
  eliminarEspacio,
  eliminarServicio,
  obtenerEspacios,
  obtenerProveedor,
  obtenerPropuestasEvento,
  obtenerServicios,
  type Espacio,
  type PropuestaProveedor,
  type ServicioExterno,
} from "../services/proveedoresAdmin";



const servicioInicial = {
  name: "",
  description: "",
};

const espacioInicial = {
  name: "",
  dimensions: "",
  base_price: 0,
  is_available: true,
};


export default function AdministracionProveedores() {
  const { usuario, token } = useAuth();
  const [proveedores, setProveedores] = useState<Proveedor[]>([]);
  const [detalle, setDetalle] = useState<Proveedor | null>(null);
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [servicios, setServicios] = useState<ServicioExterno[]>([]);
  const [espacios, setEspacios] = useState<Espacio[]>([]);
  const [propuestas, setPropuestas] = useState<PropuestaProveedor[]>([]);
  const [eventoId, setEventoId] = useState("");
  
  const [servicio, setServicio] = useState(servicioInicial);
  const [servicioEditando, setServicioEditando] = useState<string | null>(null);

  const [espacio, setEspacio] = useState(espacioInicial);
  const [espacioEditando, setEspacioEditando] = useState<string | null>(null);

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
    setEspacioEditando(null);
    setEspacio(espacioInicial);
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
  setError("");

  if (!token || !servicio.name.trim()) {
    setError("El nombre del servicio es obligatorio.");
    return;
  }

  try {
    const datos = {
      name: servicio.name.trim(),
      description: servicio.description.trim(),
    };

    const guardado = servicioEditando
      ? await actualizarServicio(servicioEditando, datos, token)
      : await crearServicio(datos, token);

    setServicios((actuales) =>
      servicioEditando
        ? actuales.map((item) =>
            item.id === guardado.id ? guardado : item
          )
        : [...actuales, guardado]
    );

    setMensaje(
      servicioEditando
        ? "Servicio actualizado correctamente."
        : "Servicio creado correctamente."
    );

    setServicio(servicioInicial);
    setServicioEditando(null);
  } catch (err) {
    setError(
      err instanceof Error
        ? err.message
        : "No se pudo guardar el servicio."
    );
  }
}

async function guardarEspacio(event: FormEvent<HTMLFormElement>) {
  event.preventDefault();
  setError("");

  if (
    !token ||
    !eventoId ||
    !espacio.name.trim() ||
    !Number.isFinite(espacio.base_price) ||
    espacio.base_price < 0
  ) {
    setError(
      "Selecciona un evento e introduce un espacio y precio válidos."
    );
    return;
  }

  try {
    const datos = {
      ...espacio,
      name: espacio.name.trim(),
      event_id: eventoId,
    };

    const guardado = espacioEditando
      ? await actualizarEspacio(espacioEditando, datos, token)
      : await crearEspacio(datos, token);

    setEspacios((actuales) =>
      espacioEditando
        ? actuales.map((item) =>
            item.id === guardado.id ? guardado : item
          )
        : [...actuales, guardado]
    );

    setMensaje(
      espacioEditando
        ? "Espacio actualizado correctamente."
        : "Espacio creado correctamente."
    );

    setEspacio(espacioInicial);
    setEspacioEditando(null);
  } catch (err) {
    setError(
      err instanceof Error
        ? err.message
        : "No se pudo guardar el espacio."
    );
  }
}


async function borrarServicio(id: string) {
  if (
    !token ||
    !window.confirm("¿Seguro que quieres eliminar este servicio?")
  ) {
    return;
  }

  setError("");

  try {
    await eliminarServicio(id, token);

    setServicios((actuales) =>
      actuales.filter((item) => item.id !== id)
    );

    if (servicioEditando === id) {
      setServicioEditando(null);
      setServicio(servicioInicial);
    }

    setMensaje("Servicio eliminado correctamente.");
  } catch (err) {
    setError(
      err instanceof Error
        ? err.message
        : "No se pudo eliminar el servicio."
    );
  }
}

async function borrarEspacio(id: string) {
  if (
    !token ||
    !window.confirm("¿Seguro que quieres eliminar este espacio?")
  ) {
    return;
  }

  setError("");

  try {
    await eliminarEspacio(id, token);

    setEspacios((actuales) =>
      actuales.filter((item) => item.id !== id)
    );

    if (espacioEditando === id) {
      setEspacioEditando(null);
      setEspacio(espacioInicial);
    }

    setMensaje("Espacio eliminado correctamente.");
  } catch (err) {
    setError(
      err instanceof Error
        ? err.message
        : "No se pudo eliminar el espacio."
    );
  }
}



  async function resolver(id: string, status: "approved" | "rejected") {
    if (!token || !window.confirm(`¿${status === "approved" ? "Aprobar" : "Rechazar"} propuesta?`)) return;
    try { await actualizarEstadoPropuesta(id, status, token); await seleccionarEvento(eventoId); setMensaje("Propuesta actualizada correctamente."); } catch (err) { setError(err instanceof Error ? err.message : "No se pudo actualizar la propuesta."); }
  }

  if (!usuario || usuario.role !== "admin" || !token) return <main className="pagina-eventos"><h1>Administración de proveedores</h1><p role="alert">Se requieren permisos de administrador.</p></main>;
  return <main className="pagina-eventos"><div className="eventos-encabezado"><p className="subtitulo">ADMINISTRACIÓN</p><h1>Proveedores y propuestas</h1><p>Empresas registradas, servicios, espacios y resoluciones.</p></div>{mensaje && <p role="status">{mensaje}</p>}{error && <p role="alert">{error}</p>}
    <section className="admin-seccion"><h2>Proveedores</h2>{proveedores.length === 0 ? <p>No hay proveedores.</p> : <ul>{proveedores.map((proveedor) => <li key={proveedor.id}>{proveedor.company_name} · {proveedor.service_category} · {proveedor.contact_email} <button type="button" onClick={() => void verDetalle(proveedor.id)}>Ver detalle</button></li>)}</ul>}{detalle && <div><h3>{detalle.company_name}</h3><p>{detalle.cif_nif} · {detalle.contact_email}</p></div>}</section>
    
<section className="admin-seccion">
  <h2>Servicios externos</h2>

  <form
    className="admin-form"
    onSubmit={(event) => void guardarServicio(event)}
  >
    <input
      aria-label="Nombre del servicio"
      required
      placeholder="Nombre"
      value={servicio.name}
      onChange={(event) =>
        setServicio({
          ...servicio,
          name: event.target.value,
        })
      }
    />

    <input
      aria-label="Descripción del servicio"
      placeholder="Descripción"
      value={servicio.description}
      onChange={(event) =>
        setServicio({
          ...servicio,
          description: event.target.value,
        })
      }
    />

    <button type="submit">
      {servicioEditando
        ? "Guardar servicio"
        : "Crear servicio"}
    </button>

    {servicioEditando && (
      <button
        type="button"
        onClick={() => {
          setServicioEditando(null);
          setServicio(servicioInicial);
        }}
      >
        Cancelar edición
      </button>
    )}
  </form>

  <ul>
    {servicios.map((item) => (
      <li key={item.id}>
        {item.name}: {item.description}

        {" "}
        <button
          type="button"
          onClick={() => {
            setServicioEditando(item.id);
            setServicio({
              name: item.name,
              description: item.description ?? "",
            });
          }}
        >
          Editar servicio
        </button>

        {" "}
        <button
          type="button"
          onClick={() => void borrarServicio(item.id)}
        >
          Eliminar servicio
        </button>
      </li>
    ))}
  </ul>
</section>

          
      <section className="admin-seccion">
        <label>
          Evento
          <select
            value={eventoId}
            onChange={(event) =>
              void seleccionarEvento(event.target.value)
            }
          >
            <option value="">Selecciona un evento</option>
            {eventos.map((evento) => (
              <option key={evento.id} value={evento.id}>
                {evento.name}
              </option>
            ))}
          </select>
        </label>

        <h2>Espacios</h2>

        <form
          className="admin-form"
          onSubmit={(event) => void guardarEspacio(event)}
        >
          <input
            aria-label="Nombre del espacio"
            required
            placeholder="Nombre"
            value={espacio.name}
            onChange={(event) =>
              setEspacio({ ...espacio, name: event.target.value })
            }
          />

          <input
            aria-label="Dimensiones del espacio"
            placeholder="Dimensiones"
            value={espacio.dimensions}
            onChange={(event) =>
              setEspacio({
                ...espacio,
                dimensions: event.target.value,
              })
            }
          />

          <input
            aria-label="Precio base del espacio"
            required
            min="0"
            step="0.01"
            type="number"
            placeholder="Precio base"
            value={espacio.base_price}
            onChange={(event) =>
              setEspacio({
                ...espacio,
                base_price: Number(event.target.value),
              })
            }
          />

          <label>
            <input
              type="checkbox"
              checked={espacio.is_available}
              onChange={(event) =>
                setEspacio({
                  ...espacio,
                  is_available: event.target.checked,
                })
              }
            />
            Disponible
          </label>

          <button type="submit">
            {espacioEditando ? "Guardar espacio" : "Crear espacio"}
          </button>

          {espacioEditando && (
            <button
              type="button"
              onClick={() => {
                setEspacioEditando(null);
                setEspacio(espacioInicial);
              }}
            >
              Cancelar edición de espacio
            </button>
          )}
        </form>

        <ul>
          {espacios.map((item) => (
            <li key={item.id}>
              {item.name} · {item.base_price.toFixed(2)} € ·{" "}
              {item.is_available ? "Disponible" : "No disponible"}

              {" "}
              <button
                type="button"
                onClick={() => {
                  setEspacioEditando(item.id);
                  setEspacio({
                    name: item.name,
                    dimensions: item.dimensions ?? "",
                    base_price: item.base_price,
                    is_available: item.is_available,
                  });
                }}
              >
                Editar espacio
              </button>

              {" "}
              <button
                type="button"
                onClick={() => void borrarEspacio(item.id)}
              >
                Eliminar espacio
              </button>
            </li>
          ))}
        </ul>

        <h2>Propuestas</h2>

        {propuestas.length === 0 ? (
          <p>No hay propuestas.</p>
        ) : (
          <ul>
            {propuestas.map((propuesta) => (
              <li key={propuesta.id}>
                {propuesta.provider_id} · {propuesta.space_id} ·{" "}
                {propuesta.budget_proposal.toFixed(2)} € ·{" "}
                {propuesta.status}

                {propuesta.status === "pending" && (
                  <>
                    {" "}
                    <button
                      type="button"
                      onClick={() =>
                        void resolver(propuesta.id, "approved")
                      }
                    >
                      Aprobar
                    </button>

                    {" "}
                    <button
                      type="button"
                      onClick={() =>
                        void resolver(propuesta.id, "rejected")
                      }
                    >
                      Rechazar
                    </button>
                  </>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
  </main>
}
