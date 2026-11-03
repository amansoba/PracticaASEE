
import { useState, type ReactNode } from "react";
import type { Usuario } from "../services/auth";
import { AuthContext } from "./AuthContextBase";

function obtenerUsuarioGuardado(): Usuario | null {
  try {
    const datos = sessionStorage.getItem("subsonic_usuario");
    return datos ? (JSON.parse(datos) as Usuario) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(
    obtenerUsuarioGuardado
  );

  const [token, setToken] = useState<string | null>(
    () => sessionStorage.getItem("subsonic_token")
  );

  function guardarSesion(nuevoUsuario: Usuario, nuevoToken: string) {
    sessionStorage.setItem(
      "subsonic_usuario",
      JSON.stringify(nuevoUsuario)
    );
    sessionStorage.setItem("subsonic_token", nuevoToken);

    setUsuario(nuevoUsuario);
    setToken(nuevoToken);
  }

  function cerrarSesion() {
    sessionStorage.removeItem("subsonic_usuario");
    sessionStorage.removeItem("subsonic_token");

    setUsuario(null);
    setToken(null);
  }

  return (
    <AuthContext.Provider
      value={{ usuario, token, guardarSesion, cerrarSesion }}
    >
      {children}
    </AuthContext.Provider>
  );
}
