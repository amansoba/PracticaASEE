import { useEffect, useState } from "react";
import { useAuth } from "../context/useAuth";
import { listarUsuarios, actualizarRol, type Usuario } from "../services/usuarios";

const ROLES: Usuario["role"][] = ["client", "provider", "admin"];

export default function AdminUsuarios() {
  const { usuario } = useAuth();
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (usuario?.role !== "admin") return;
    listarUsuarios()
      .then(setUsuarios)
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Error al cargar usuarios");
      })
      .finally(() => {
        setCargando(false);
      });
  }, [usuario]);

  async function cambiarRol(id: string, nuevoRol: Usuario["role"]) {
    setError("");
    try {
      await actualizarRol(id, nuevoRol);
      const datos = await listarUsuarios();
      setUsuarios(datos);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cambiar el rol");
    }
  }

  if (!usuario || usuario.role !== "admin") {
    return (
      <main className="pagina-eventos">
        <h1>Usuarios</h1>
        <p>Esta sección es solo para administradores.</p>
      </main>
    );
  }

  return (
    <main className="pagina-eventos">
      <div className="eventos-encabezado">
        <p className="subtitulo">ADMINISTRACIÓN</p>
        <h1>Gestión de usuarios</h1>
      </div>

      {error && <p className="login-error">{error}</p>}
      {cargando && <p>Cargando usuarios...</p>}

      {!cargando && (
        <div className="eventos-grid">
          {usuarios.map((u) => (
            <article className="evento-card" key={u.id}>
              <div className="evento-card-contenido">
                <h3>{u.name}</h3>
                <p>{u.email}</p>
                <p className="pedido-identificador">{u.id}</p>
                <label style={{ marginTop: 16, display: "block" }}>Rol</label>
                <select
                  value={u.role}
                  onChange={(e) =>
                    cambiarRol(u.id, e.target.value as Usuario["role"])
                  }
                  disabled={u.id === usuario.id}
                >
                  {ROLES.map((rol) => (
                    <option key={rol} value={rol}>
                      {rol}
                    </option>
                  ))}
                </select>
                {u.id === usuario.id && (
                  <p className="pedido-identificador">No puedes editarte a ti mismo</p>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}
