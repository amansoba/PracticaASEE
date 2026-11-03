
import { createContext } from "react";
import type { Usuario } from "../services/auth";

export interface AuthContextType {
  usuario: Usuario | null;
  token: string | null;
  guardarSesion: (usuario: Usuario, token: string) => void;
  cerrarSesion: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(
  undefined
);
