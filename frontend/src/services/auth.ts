
export interface Usuario {
  id: string;
  name: string;
  email: string;
  role: "client" | "provider" | "admin";
  phone: string | null;
  avatar_url: string | null;
}

export interface RespuestaLogin {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: Usuario;
}

export async function iniciarSesion(
  email: string,
  password: string
): Promise<RespuestaLogin> {
  const respuesta = await fetch("/api/auth/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!respuesta.ok) {
    if (respuesta.status === 401) {
      throw new Error("Correo electrónico o contraseña incorrectos");
    }

    throw new Error("No se pudo iniciar sesión");
  }

  return respuesta.json();
}


export async function finalizarSesion(token: string): Promise<void> {
  const respuesta = await fetch("/api/auth/auth/logout", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!respuesta.ok) {
    throw new Error("No se pudo cerrar la sesión en el servidor");
  }
}


export interface DatosRegistro {
  name: string;
  email: string;
  password: string;
  phone?: string;
}

export async function registrarUsuario(
  datos: DatosRegistro
): Promise<Usuario> {
  const respuesta = await fetch("/api/auth/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(datos),
  });

  if (!respuesta.ok) {
    if (respuesta.status === 400) {
      throw new Error("Datos inválidos o correo electrónico ya registrado");
    }

    throw new Error("No se pudo registrar el usuario");
  }

  return respuesta.json();
}
