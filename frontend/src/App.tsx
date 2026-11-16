import { Route, Routes } from "react-router-dom";
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

function Inicio() {
  return (
    <main className="pagina-inicio">
      <p className="subtitulo">LA EXPERIENCIA MUSICAL DEFINITIVA</p>
      <h1>VIVE LA MÚSICA SIN LÍMITES</h1>
      <p>
        Descubre festivales, artistas y experiencias únicas
        con Subsonic Festival.
      </p>
    </main>
  );
}

function App() {
  return (
    <>
      <Navbar />

      <Routes>
        <Route path="/" element={<Inicio />} />
        <Route path="/login" element={<Login />} />
        <Route path="/registro" element={<Registro />} />
        <Route path="/recuperar-contrasena" element={<RecuperarContrasena />} />
        <Route path="/recuperar-contrasena/confirmar" element={<ConfirmarContrasena />} />

        <Route path="/eventos" element={<Eventos />} />
        <Route path="/eventos/:id" element={<EventoDetalle />} />
        <Route path="/artistas" element={<Artistas />} />
        <Route path="/tienda" element={<Tienda />} />
        <Route path="/carrito" element={<Carrito />} />
        <Route path="/mis-pedidos" element={<MisPedidos />} />
        <Route path="/mis-pedidos/:id" element={<PedidoDetalle />} />
        <Route path="/mis-entradas" element={<MisEntradas />} />
        <Route path="/proveedores" element={<Proveedores />} />
        <Route path="/perfil" element={<Perfil />} />

        <Route path="/admin/eventos" element={<AdminEventos />} />
        <Route path="/admin/usuarios" element={<AdminUsuarios />} />

        <Route path="*" element={<main className="pagina-eventos"><h1>404</h1><p>Página no encontrada.</p></main>} />
      </Routes>
    </>
  );
}

export default App;
