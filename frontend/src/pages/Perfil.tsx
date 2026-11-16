import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { obtenerMiPerfil, actualizarMiPerfil, type DatosPerfil } from "../services/usuarios";
import type { Usuario } from "../services/auth";

export default function Perfil() {
  const { usuario, guardarSesion } = useAuth();
  const [perfil, setPerfil] = useState<Usuario | null>(null);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [exito, setExito] = useState("");

  useEffect(() => {
    let activo = true;

    async function cargar() {
      try {
        const datos = await obtenerMiPerfil();
        if (!activo) return;
        setPerfil(datos);
        setName(datos.name);
        setPhone(datos.phone || "");
        setAvatarUrl(datos.avatar_url || "");
      } catch (err) {
        if (activo) {
          setError(err instanceof Error ? err.message : "Error al cargar el perfil");
        }
      } finally {
        if (activo) setCargando(false);
      }
    }

    void cargar();

    return () => {
      activo = false;
    };
  }, []);

  async function guardar(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setExito("");
    setGuardando(true);

    const datos: DatosPerfil = {
      name: name.trim() || undefined,
      phone: phone.trim() || null,
      avatar_url: avatarUrl.trim() || null,
    };

    try {
      const actualizado = await actualizarMiPerfil(datos);
      setPerfil(actualizado);
      if (usuario) {
        guardarSesion(actualizado, sessionStorage.getItem("subsonic_token") || "");
      }
      setExito("Perfil actualizado correctamente");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al actualizar el perfil");
    } finally {
      setGuardando(false);
    }
  }

  if (!usuario) {
    return (
      <main className="pagina-eventos">
        <h1>Perfil</h1>
        <p>Debes iniciar sesión para ver tu perfil.</p>
        <Link to="/login" className="navbar-login">Iniciar sesión</Link>
      </main>
    );
  }

  return (
    <main className="pagina-eventos">
      <div className="eventos-encabezado">
        <p className="subtitulo">TU CUENTA</p>
        <h1>Perfil</h1>
      </div>

      {cargando && <p>Cargando perfil...</p>}
      {error && <p className="login-error">{error}</p>}
      {exito && <p className="registro-exito">{exito}</p>}

      {!cargando && perfil && (
        <form className="login-formulario" onSubmit={guardar}>
          <p>
            <strong>Email:</strong> {perfil.email}
          </p>
          <p>
            <strong>Rol:</strong> {perfil.role}
          </p>

          <label htmlFor="perfil-nombre">Nombre</label>
          <input
            id="perfil-nombre"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />

          <label htmlFor="perfil-telefono">Teléfono</label>
          <input
            id="perfil-telefono"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />

          <label htmlFor="perfil-avatar">URL de avatar</label>
          <input
            id="perfil-avatar"
            value={avatarUrl}
            onChange={(e) => setAvatarUrl(e.target.value)}
          />

          <button type="submit" disabled={guardando}>
            {guardando ? "Guardando..." : "Guardar cambios"}
          </button>

          <p className="registro-enlace">
            <Link to="/recuperar-contrasena">Cambiar contraseña</Link>
          </p>
        </form>
      )}
    </main>
  );
}
