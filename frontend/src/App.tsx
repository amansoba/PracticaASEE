
import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import "./App.css";
import Eventos from "./pages/Eventos";
import Artistas from "./pages/Artistas";
import Tienda from "./pages/Tienda";
import Login from "./pages/Login";
import MisPedidos from "./pages/MisPedidos";
import Registro from "./pages/Registro";
import Proveedores from "./pages/Proveedores";

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
        <Route path="/eventos" element={<Eventos />} />
        <Route path="/artistas" element={<Artistas />} />
        <Route path="/tienda" element={<Tienda />} />
        <Route path="/proveedores" element={<Proveedores />} />
        <Route path="/mis-pedidos" element={<MisPedidos />} />
        <Route path="/registro" element={<Registro />} />
      </Routes>
    </>
  );
}

export default App;
