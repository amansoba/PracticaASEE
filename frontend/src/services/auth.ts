import { api } from "./api";

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

export interface DatosRegistro {
  name: string;
  email: string;
  password: string;
  phone?: string;
}

export async function iniciarSesion(
  email: string,
  password: string
): Promise<RespuestaLogin> {
  return api.post("/api/auth/auth/login", { email, password });
}

export async function finalizarSesion(): Promise<void> {
  return api.post("/api/auth/auth/logout", {});
}

export async function registrarUsuario(
  datos: DatosRegistro
): Promise<Usuario> {
  return api.post("/api/auth/auth/register", datos);
}

export async function solicitarRecuperacion(email: string): Promise<void> {
  return api.post("/api/auth/auth/reset-password", { email });
}

export interface DatosConfirmarRecuperacion {
  token: string;
  new_password: string;
}

export async function confirmarRecuperacion(
  datos: DatosConfirmarRecuperacion
): Promise<void> {
  return api.post("/api/auth/auth/reset-password/confirm", datos);
}
