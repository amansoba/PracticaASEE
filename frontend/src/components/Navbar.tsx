
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { finalizarSesion } from "../services/auth";


function Navbar() {
  const { usuario, cerrarSesion } = useAuth();
  const navigate = useNavigate();


  async function manejarCierreSesion() {
    try {
      await finalizarSesion();
    } catch (error) {
      console.error(
        "Error al revocar la sesión:",
        error
      );
    } finally {
      cerrarSesion();
      navigate("/login");
    }
  }


  return (
    <header className="navbar">
      <Link to="/" className="navbar-logo">
        SUBSONIC<span>FESTIVAL</span>
      </Link>

      <nav className="navbar-links">
        <NavLink to="/" end>
          Inicio
        </NavLink>

        <NavLink to="/eventos">
          Eventos
        </NavLink>

        <NavLink to="/artistas">
          Artistas
        </NavLink>

        <NavLink to="/tienda">
          Tienda
        </NavLink>

        {/* Opciones de cliente */}
        {usuario?.role === "client" && (
          <>
            <NavLink to="/carrito">
              Carrito
            </NavLink>

            <NavLink to="/mis-entradas">
              Mis entradas
            </NavLink>

            <NavLink to="/mis-pedidos">
              Mis pedidos
            </NavLink>
          </>
        )}

        <NavLink to="/proveedores">
          Proveedores
        </NavLink>

        {/* Opciones de administrador */}
        {usuario?.role === "admin" && (
          <>
            <NavLink to="/admin/eventos">
              Admin eventos
            </NavLink>

            <NavLink to="/admin/usuarios">
              Usuarios
            </NavLink>

            <NavLink to="/admin/catalogo">
              Admin catálogo
            </NavLink>

            <NavLink to="/admin/comercio">
              Admin comercio
            </NavLink>

            <NavLink to="/admin/proveedores">
              Admin proveedores
            </NavLink>
          </>
        )}

        {/* Opciones de proveedor */}
        {usuario?.role === "provider" && (
          <NavLink to="/portal/proveedor">
            Mi portal
          </NavLink>
        )}
      </nav>

      {usuario ? (
        <div className="navbar-usuario">
          <div className="navbar-usuario-info">
            <Link to="/perfil">
              <strong>{usuario.name}</strong>
            </Link>

            <span>{usuario.role}</span>
          </div>

          <button
            className="navbar-logout"
            onClick={manejarCierreSesion}
          >
            Cerrar sesión
          </button>
        </div>
      ) : (
        <Link to="/login" className="navbar-login">
          Iniciar sesión
        </Link>
      )}
    </header>
  );
}

export default Navbar;
