import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import type { Usuario } from "../services/auth";
import {
  obtenerProveedores,
  obtenerMiEmpresa,
  obtenerPropuestasProveedor,
  type Proveedor,
  type PropuestaProveedor,
} from "../services/proveedores";

interface PanelProveedoresProps {
  usuario: Usuario;
}

function PanelProveedores({ usuario }: PanelProveedoresProps) {
  const [proveedores, setProveedores] = useState<Proveedor[]>([]);
  const [miEmpresa, setMiEmpresa] = useState<Proveedor | null>(null);
  const [propuestas, setPropuestas] = useState<PropuestaProveedor[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let activo = true;

    async function cargarDatos() {
      try {
        if (usuario.role === "admin") {
          const datos = await obtenerProveedores();
          if (activo) setProveedores(datos);
        } else if (usuario.role === "provider") {
          const empresa = await obtenerMiEmpresa();
          if (!activo) return;
          setMiEmpresa(empresa);

          const datos = await obtenerPropuestasProveedor(empresa.id);
          if (activo) setPropuestas(datos);
        }
      } catch (err) {
        if (activo) {
          setError(
            err instanceof Error
              ? err.message
              : "No se pudieron cargar los datos"
          );
        }
      } finally {
        if (activo) setCargando(false);
      }
    }

    void cargarDatos();

    return () => {
      activo = false;
    };
  }, [usuario]);

  if (usuario.role === "provider") {
    return (
      <main className="pagina-eventos">
        <div className="eventos-encabezado">
          <p className="subtitulo">ÁREA DE PROVEEDORES</p>
          <h1>Panel de proveedores</h1>
          <p>
            Consulta los datos de tu empresa y las propuestas
            realizadas para los festivales.
          </p>
        </div>

        {cargando && <p>Cargando información...</p>}
        {error && <p role="alert">{error}</p>}

        {miEmpresa && (
          <section>
            <h2>Mi empresa</h2>
            <div className="eventos-grid">
              <article className="evento-card">
                <div className="evento-card-contenido">
                  <span className="evento-etiqueta">
                    {miEmpresa.service_category}
                  </span>
                  <h2>{miEmpresa.company_name}</h2>
                  <p>CIF/NIF: {miEmpresa.cif_nif}</p>
                  <p>
                    Contacto:{" "}
                    {miEmpresa.contact_email || "No especificado"}
                  </p>
                  <p className="pedido-identificador">ID: {miEmpresa.id}</p>
                </div>
              </article>
            </div>
          </section>
        )}

        {miEmpresa && !error && (
          <section>
            <h2>Mis propuestas</h2>
            {!cargando && propuestas.length === 0 && (
              <p>Todavía no tienes propuestas registradas.</p>
            )}
            <div className="eventos-grid">
              {propuestas.map((propuesta) => (
                <article className="evento-card" key={propuesta.id}>
                  <div className="evento-card-contenido">
                    <span className="evento-etiqueta">{propuesta.status}</span>
                    <h2>Propuesta de presupuesto</h2>
                    <p>Evento: {propuesta.event_id}</p>
                    <p>
                      Presupuesto:{" "}
                      {propuesta.budget_proposal.toFixed(2)} €
                    </p>
                    {propuesta.setup_date && (
                      <p>Fecha de montaje: {propuesta.setup_date}</p>
                    )}
                    <p className="pedido-identificador">ID: {propuesta.id}</p>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}
      </main>
    );
  }

  return (
    <main className="pagina-eventos">
      <div className="eventos-encabezado">
        <p className="subtitulo">ADMINISTRACIÓN SUBSONIC</p>
        <h1>Gestión de proveedores</h1>
        <p>Consulta las empresas proveedoras registradas.</p>
      </div>

      {cargando && <p>Cargando proveedores...</p>}
      {error && <p role="alert">{error}</p>}
      {!cargando && !error && proveedores.length === 0 && (
        <p>No hay proveedores registrados.</p>
      )}

      <div className="eventos-grid">
        {proveedores.map((proveedor) => (
          <article className="evento-card" key={proveedor.id}>
            <div className="evento-card-contenido">
              <span className="evento-etiqueta">
                {proveedor.service_category}
              </span>
              <h2>{proveedor.company_name}</h2>
              <p>CIF/NIF: {proveedor.cif_nif}</p>
              <p>
                Contacto:{" "}
                {proveedor.contact_email || "No especificado"}
              </p>
              <p className="pedido-identificador">ID: {proveedor.id}</p>
            </div>
          </article>
        ))}
      </div>
    </main>
  );
}

function Proveedores() {
  const { usuario } = useAuth();

  if (!usuario) {
    return (
      <main className="pagina-eventos">
        <h1>Proveedores</h1>
        <p>Inicia sesión para acceder a esta sección.</p>
        <Link to="/login" className="navbar-login">
          Iniciar sesión
        </Link>
      </main>
    );
  }

  if (usuario.role === "client") {
    return (
      <main className="pagina-eventos">
        <h1>Proveedores</h1>
        <p>Esta sección está reservada a proveedores y administradores.</p>
      </main>
    );
  }

  return <PanelProveedores usuario={usuario} />;
}

export default Proveedores;
