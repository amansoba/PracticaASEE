
import {
  createContext,
  useContext,
  useState,
  type ReactNode,
} from "react";
import type { Usuario } from "../services/auth";

interface AuthContextType {
  usuario: Usuario | null;
  token: string | null;
  guardarSesion: (usuario: Usuario, token: string) => void;
  cerrarSesion: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

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

export function useAuth() {
  const contexto = useContext(AuthContext);

  if (!contexto) {
    throw new Error("useAuth debe utilizarse dentro de AuthProvider");
  }

  return contexto;
}
