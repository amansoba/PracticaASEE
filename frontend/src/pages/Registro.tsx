
import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registrarUsuario } from "../services/auth";

function Registro() {
  const navigate = useNavigate();

  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmarPassword, setConfirmarPassword] = useState("");
  const [telefono, setTelefono] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  async function manejarRegistro(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setError("");

    if (password.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres");
      return;
    }

    if (password !== confirmarPassword) {
      setError("Las contraseñas no coinciden");
      return;
    }

    setCargando(true);

    try {
      await registrarUsuario({
        name: nombre.trim(),
        email: email.trim(),
        password,
        ...(telefono.trim() ? { phone: telefono.trim() } : {}),
      });

      navigate("/login", {
        state: {
          mensaje: "Cuenta creada correctamente. Ya puedes iniciar sesión.",
        },
      });
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Error al registrar el usuario"
      );
    } finally {
      setCargando(false);
    }
  }

  return (
    <main className="pagina-login">
      <form className="login-formulario" onSubmit={manejarRegistro}>
        <p className="subtitulo">ÚNETE A SUBSONIC</p>
        <h1>Crear cuenta</h1>
        <p>Regístrate para disfrutar de Subsonic Festival.</p>

        <label htmlFor="registro-nombre">Nombre completo</label>
        <input
          id="registro-nombre"
          type="text"
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          placeholder="Tu nombre"
          autoComplete="name"
          required
        />

        <label htmlFor="registro-email">Correo electrónico</label>
        <input
          id="registro-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="usuario@email.com"
          autoComplete="email"
          required
        />

        <label htmlFor="registro-password">Contraseña</label>
        <input
          id="registro-password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Mínimo 8 caracteres"
          autoComplete="new-password"
          minLength={8}
          required
        />

        <label htmlFor="registro-confirmar">Confirmar contraseña</label>
        <input
          id="registro-confirmar"
          type="password"
          value={confirmarPassword}
          onChange={(e) => setConfirmarPassword(e.target.value)}
          placeholder="Repite la contraseña"
          autoComplete="new-password"
          minLength={8}
          required
        />

        <label htmlFor="registro-telefono">Teléfono (opcional)</label>
        <input
          id="registro-telefono"
          type="tel"
          value={telefono}
          onChange={(e) => setTelefono(e.target.value)}
          placeholder="Número de contacto"
          autoComplete="tel"
        />

        {error && <p className="login-error" role="alert">{error}</p>}

        <button type="submit" disabled={cargando}>
          {cargando ? "Creando cuenta..." : "Crear cuenta"}
        </button>

        <p className="registro-enlace">
          ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
        </p>
      </form>
    </main>
  );
}

export default Registro;
