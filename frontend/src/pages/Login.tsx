import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { iniciarSesion } from "../services/auth";
import { useAuth } from "../context/useAuth";

function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { guardarSesion } = useAuth();

  const mensajeRegistro = (
    location.state as { mensaje?: string } | null
  )?.mensaje;

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  async function manejarLogin(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setError("");
    setCargando(true);

    try {
      const resultado = await iniciarSesion(email, password);

      guardarSesion(resultado.user, resultado.access_token);

      navigate("/", { replace: true });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Error al iniciar sesión"
      );
    } finally {
      setCargando(false);
    }
  }

  return (
    <main className="pagina-login">
      <form className="login-formulario" onSubmit={manejarLogin}>
        <p className="subtitulo">BIENVENIDO A SUBSONIC</p>

        <h1>Iniciar sesión</h1>

        <p>Accede a tu cuenta para disfrutar del festival.</p>

        {mensajeRegistro && (
          <p className="registro-exito" role="status">
            {mensajeRegistro}
          </p>
        )}

        <label htmlFor="email">Correo electrónico</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(evento) => setEmail(evento.target.value)}
          placeholder="usuario@email.com"
          autoComplete="username"
          required
        />

        <label htmlFor="password">Contraseña</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(evento) => setPassword(evento.target.value)}
          placeholder="Introduce tu contraseña"
          autoComplete="current-password"
          required
        />

        {error && (
          <p className="login-error" role="alert">
            {error}
          </p>
        )}

        <button type="submit" disabled={cargando}>
          {cargando ? "Iniciando..." : "Entrar"}
        </button>

        <p className="registro-enlace">
          ¿No tienes cuenta? <Link to="/registro">Regístrate</Link>
        </p>
        <p className="registro-enlace">
          <Link to="/recuperar-contrasena">¿Has olvidado tu contraseña?</Link>
        </p>
      </form>
    </main>
  );
}

export default Login;
