
import type { ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/useAuth";

import Navbar from "./components/Navbar";
import "./App.css";

import Eventos from "./pages/Eventos";
import EventoDetalle from "./pages/EventoDetalle";
import Artistas from "./pages/Artistas";
import Tienda from "./pages/Tienda";
import Carrito from "./pages/Carrito";
import Login from "./pages/Login";
import MisPedidos from "./pages/MisPedidos";
import PedidoDetalle from "./pages/PedidoDetalle";
import MisEntradas from "./pages/MisEntradas";
import Registro from "./pages/Registro";
import Proveedores from "./pages/Proveedores";
import Perfil from "./pages/Perfil";
import RecuperarContrasena from "./pages/RecuperarContrasena";
import ConfirmarContrasena from "./pages/ConfirmarContrasena";

import AdminEventos from "./pages/AdminEventos";
import AdminUsuarios from "./pages/AdminUsuarios";

import AdministracionCatalogo from "./pages/AdministracionCatalogo";
import AdministracionComercio from "./pages/AdministracionComercio";
import AdministracionProveedores from "./pages/AdministracionProveedores";
import PortalProveedor from "./pages/PortalProveedor";


function Inicio() {
  return (
    <main className="pagina-inicio">
      <p className="subtitulo">
        LA EXPERIENCIA MUSICAL DEFINITIVA
      </p>

      <h1>VIVE LA MÚSICA SIN LÍMITES</h1>

      <p>
        Descubre festivales, artistas y experiencias únicas
        con Subsonic Festival.
      </p>
    </main>
  );
}


// ============================================================
// PROTECCION DE RUTAS SEGUN EL ROL
// ============================================================

function RutaProtegida({
  rol,
  children
}: {
  rol: "admin" | "provider";
  children: ReactNode;
}) {
  const { usuario } = useAuth();

  if (!usuario) {
    return <Navigate to="/login" replace />;
  }

  if (usuario.role !== rol) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}


// ============================================================
// APLICACION
// ============================================================

function App() {
  return (
    <>
      <Navbar />

      <Routes>
        {/* Rutas generales */}
        <Route path="/" element={<Inicio />} />
        <Route path="/login" element={<Login />} />
        <Route path="/registro" element={<Registro />} />

        <Route
          path="/recuperar-contrasena"
          element={<RecuperarContrasena />}
        />

        <Route
          path="/recuperar-contrasena/confirmar"
          element={<ConfirmarContrasena />}
        />

        <Route path="/eventos" element={<Eventos />} />
        <Route
          path="/eventos/:id"
          element={<EventoDetalle />}
        />

        <Route path="/artistas" element={<Artistas />} />
        <Route path="/tienda" element={<Tienda />} />
        <Route path="/carrito" element={<Carrito />} />

        <Route
          path="/mis-pedidos"
          element={<MisPedidos />}
        />

        <Route
          path="/mis-pedidos/:id"
          element={<PedidoDetalle />}
        />

        <Route
          path="/mis-entradas"
          element={<MisEntradas />}
        />

        <Route
          path="/proveedores"
          element={<Proveedores />}
        />

        <Route path="/perfil" element={<Perfil />} />

        {/* Rutas de administrador */}
        <Route
          path="/admin/eventos"
          element={
            <RutaProtegida rol="admin">
              <AdminEventos />
            </RutaProtegida>
          }
        />

        <Route
          path="/admin/usuarios"
          element={
            <RutaProtegida rol="admin">
              <AdminUsuarios />
            </RutaProtegida>
          }
        />

        <Route
          path="/admin/catalogo"
          element={
            <RutaProtegida rol="admin">
              <AdministracionCatalogo />
            </RutaProtegida>
          }
        />

        <Route
          path="/admin/comercio"
          element={
            <RutaProtegida rol="admin">
              <AdministracionComercio />
            </RutaProtegida>
          }
        />

        <Route
          path="/admin/proveedores"
          element={
            <RutaProtegida rol="admin">
              <AdministracionProveedores />
            </RutaProtegida>
          }
        />

        {/* Portal exclusivo del proveedor */}
        <Route
          path="/portal/proveedor"
          element={
            <RutaProtegida rol="provider">
              <PortalProveedor />
            </RutaProtegida>
          }
        />

        {/* Ruta inexistente */}
        <Route
          path="*"
          element={
            <main className="pagina-eventos">
              <h1>404</h1>
              <p>Página no encontrada.</p>
            </main>
          }
        />
      </Routes>
    </>
  );
}

export default App;
