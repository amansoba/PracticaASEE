import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { solicitarRecuperacion } from "../services/auth";

export default function RecuperarContrasena() {
  const [email, setEmail] = useState("");
  const [enviado, setEnviado] = useState(false);
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  async function enviar(e: FormEvent) {
    e.preventDefault();
    setError("");
    setCargando(true);

    try {
      await solicitarRecuperacion(email);
      setEnviado(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al solicitar la recuperación");
    } finally {
      setCargando(false);
    }
  }

  return (
    <main className="pagina-login">
      <form className="login-formulario" onSubmit={enviar}>
        <p className="subtitulo">RECUPERAR ACCESO</p>
        <h1>Recuperar contraseña</h1>

        {enviado ? (
          <>
            <p className="registro-exito" role="status">
              Si existe una cuenta con ese correo, recibirás instrucciones.
            </p>
            <p className="registro-enlace">
              <Link to="/login">Volver al inicio de sesión</Link>
            </p>
          </>
        ) : (
          <>
            <p>Introduce tu correo y te enviaremos un enlace.</p>

            <label htmlFor="recuperacion-email">Correo electrónico</label>
            <input
              id="recuperacion-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            {error && <p className="login-error">{error}</p>}

            <button type="submit" disabled={cargando}>
              {cargando ? "Enviando..." : "Enviar enlace"}
            </button>

            <p className="registro-enlace">
              <Link to="/login">Cancelar</Link>
            </p>
          </>
        )}
      </form>
    </main>
  );
}
