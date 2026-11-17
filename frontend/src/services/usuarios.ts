import { api } from "./api";
import type { Usuario } from "./auth";

export type { Usuario };

export interface DatosPerfil {
  name?: string;
  phone?: string | null;
  avatar_url?: string | null;
}

export async function obtenerMiPerfil(): Promise<Usuario> {
  return api.get("/api/auth/users/me");
}

export async function actualizarMiPerfil(
  datos: DatosPerfil
): Promise<Usuario> {
  return api.put("/api/auth/users/me", datos);
}

export async function listarUsuarios(): Promise<Usuario[]> {
  return api.get("/api/auth/users");
}

export async function obtenerUsuario(id: string): Promise<Usuario> {
  return api.get(`/api/auth/users/${encodeURIComponent(id)}`);
}

export async function actualizarRol(
  id: string,
  role: "client" | "provider" | "admin"
): Promise<void> {
  return api.put(`/api/auth/users/${encodeURIComponent(id)}/role`, { role });
}
