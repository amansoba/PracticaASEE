import { useState, type FormEvent } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import { confirmarRecuperacion } from "../services/auth";

export default function ConfirmarContrasena() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const tokenInicial = searchParams.get("token") || "";

  const [token, setToken] = useState(tokenInicial);
  const [password, setPassword] = useState("");
  const [confirmar, setConfirmar] = useState("");
  const [error, setError] = useState("");
  const [exito, setExito] = useState(false);
  const [cargando, setCargando] = useState(false);

  async function enviar(e: FormEvent) {
    e.preventDefault();
    setError("");

    if (password.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres");
      return;
    }

    if (password !== confirmar) {
      setError("Las contraseñas no coinciden");
      return;
    }

    setCargando(true);

    try {
      await confirmarRecuperacion({ token, new_password: password });
      setExito(true);
      setTimeout(() => navigate("/login"), 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cambiar la contraseña");
    } finally {
      setCargando(false);
    }
  }

  return (
    <main className="pagina-login">
      <form className="login-formulario" onSubmit={enviar}>
        <p className="subtitulo">NUEVA CONTRASEÑA</p>
        <h1>Restablecer contraseña</h1>

        {exito ? (
          <p className="registro-exito" role="status">
            Contraseña actualizada. Redirigiendo al login...
          </p>
        ) : (
          <>
            <label htmlFor="token">Token de recuperación</label>
            <input
              id="token"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              required
            />

            <label htmlFor="nueva-password">Nueva contraseña</label>
            <input
              id="nueva-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <label htmlFor="confirmar-password">Confirmar contraseña</label>
            <input
              id="confirmar-password"
              type="password"
              value={confirmar}
              onChange={(e) => setConfirmar(e.target.value)}
              required
            />

            {error && <p className="login-error">{error}</p>}

            <button type="submit" disabled={cargando}>
              {cargando ? "Guardando..." : "Cambiar contraseña"}
            </button>

            <p className="registro-enlace">
              <Link to="/login">Volver al login</Link>
            </p>
          </>
        )}
      </form>
    </main>
  );
}
