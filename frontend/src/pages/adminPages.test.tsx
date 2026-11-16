import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthProvider } from "../context/AuthContext";
import AdministracionCatalogo from "./AdministracionCatalogo";
import AdministracionComercio from "./AdministracionComercio";
import AdministracionProveedores from "./AdministracionProveedores";
import PortalProveedor from "./PortalProveedor";

function sesion(role: "admin" | "provider") {
  sessionStorage.setItem("subsonic_token", "test-token");
  sessionStorage.setItem("subsonic_usuario", JSON.stringify({ id: "u1", name: "Test", email: "test@example.com", role, phone: null, avatar_url: null }));
}

function respuesta(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

beforeEach(() => {
  sessionStorage.clear();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("protección y catálogo administrativo", () => {
  it("rechaza a un cliente", () => {
    render(<AuthProvider><AdministracionCatalogo /></AuthProvider>);
    expect(screen.getByRole("alert")).toHaveTextContent("administrador");
  });

  it("filtra, crea, edita y elimina artistas", async () => {
    sesion("admin");
    const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation(async (_input, init) => {
      if (init?.method === "POST") return respuesta({ id: "a2", name: "Nuevo", genre: "Rock" }, 201);
      if (init?.method === "PUT") return respuesta({ id: "a1", name: "Editado", genre: "Rock" });
      if (init?.method === "DELETE") return new Response(null, { status: 204 });
      return respuesta([{ id: "a1", name: "Daft Punk", genre: "Electrónica", biography: null, image_url: null }]);
    });
    render(<AuthProvider><AdministracionCatalogo /></AuthProvider>);
    await screen.findByText("Daft Punk");

    fireEvent.change(screen.getByLabelText("Filtrar por género"), { target: { value: "Rock" } });
    await waitFor(() => expect(String(fetchMock.mock.calls.at(-1)?.[0])).toContain("genre=Rock"));

    fireEvent.change(screen.getByLabelText("Nombre"), { target: { value: "Nuevo" } });
    fireEvent.change(screen.getAllByLabelText("Género")[0], { target: { value: "Rock" } });
    fireEvent.click(screen.getByRole("button", { name: "Crear artista" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith("/api/catalogo/artists", expect.objectContaining({ method: "POST" })));

    fireEvent.click(screen.getByRole("button", { name: "Editar" }));
    fireEvent.change(screen.getByLabelText("Nombre"), { target: { value: "Editado" } });
    fireEvent.click(screen.getByRole("button", { name: "Guardar cambios" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith("/api/catalogo/artists/a1", expect.objectContaining({ method: "PUT" })));

    vi.spyOn(window, "confirm").mockReturnValue(true);
    fireEvent.click(screen.getByRole("button", { name: "Eliminar" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith("/api/catalogo/artists/a1", expect.objectContaining({ method: "DELETE" })));
  });

  it("crea una canción con campos Spotify opcionales", async () => {
    sesion("admin");
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
      if (String(input).includes("/songs") && init?.method === "POST") return respuesta({ id: "s1", artist_id: "a1", title: "Tema" }, 201);
      if (String(input).includes("/songs")) return respuesta([]);
      return respuesta([{ id: "a1", name: "Artista", genre: "Rock", biography: null, image_url: null }]);
    });
    render(<AuthProvider><AdministracionCatalogo /></AuthProvider>);
    await screen.findByText("Artista");
    fireEvent.click(screen.getByRole("button", { name: "Canciones" }));
    fireEvent.change(screen.getByLabelText("Título"), { target: { value: "Tema" } });
    fireEvent.change(screen.getByLabelText("Spotify ID"), { target: { value: "spotify1" } });
    fireEvent.change(screen.getByLabelText("Spotify URL"), { target: { value: "https://open.spotify.com/track/spotify1" } });
    fireEvent.change(screen.getByLabelText("Preview URL"), { target: { value: "https://cdn.example/preview.mp3" } });
    fireEvent.click(screen.getByRole("button", { name: "Añadir canción" }));
    await waitFor(() => expect(globalThis.fetch).toHaveBeenCalledWith("/api/catalogo/artists/a1/songs", expect.objectContaining({ method: "POST", body: expect.stringContaining("spotify_id") })));
  });
});

describe("comercio administrativo", () => {
  it("crea y edita productos y bloquea tallas duplicadas", async () => {
    sesion("admin");
    const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation(async (_input, init) => {
      if (init?.method === "POST") return respuesta({ id: "p2", name: "Camiseta", category: "ropa", price: 20, variants: [{ size: "M", stock: 3 }] }, 201);
      if (init?.method === "PUT") return respuesta({ id: "p1", name: "Camiseta", category: "ropa", price: 21, variants: [{ size: "M", stock: 4 }] });
      return respuesta([{ id: "p1", name: "Camiseta", description: "", category: "ropa", price: 20, images: [], variants: [{ size: "M", stock: 3 }] }]);
    });
    render(<AuthProvider><AdministracionComercio /></AuthProvider>);
    await screen.findByText("Camiseta");
    fireEvent.change(screen.getByLabelText("Nombre"), { target: { value: "Nueva camiseta" } });
    fireEvent.change(screen.getByLabelText("Categoría"), { target: { value: "ropa" } });
    fireEvent.change(screen.getByLabelText("Precio"), { target: { value: "20" } });
    fireEvent.change(screen.getByLabelText("Nueva talla"), { target: { value: "L" } });
    fireEvent.change(screen.getByLabelText("Nuevo stock"), { target: { value: "3" } });
    fireEvent.click(screen.getByRole("button", { name: "Añadir variante" }));
    fireEvent.click(screen.getByRole("button", { name: "Guardar producto" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith("/api/tienda/products", expect.objectContaining({ method: "POST" })));

    fireEvent.click(screen.getByRole("button", { name: "Editar" }));
    fireEvent.change(screen.getByLabelText("Precio"), { target: { value: "21" } });
    fireEvent.click(screen.getByRole("button", { name: "Guardar producto" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith("/api/tienda/products/p1", expect.objectContaining({ method: "PUT" })));
  });

  it("limpia el pedido anterior cuando falla una nueva consulta", async () => {
    sesion("admin");
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => String(input).includes("orders") ? respuesta({ id: "o1", user_id: "u1", items: [], total_price: 10, status: "paid", created_at: "2026-01-01" }) : respuesta([]));
    render(<AuthProvider><AdministracionComercio /></AuthProvider>);
    fireEvent.change(screen.getByLabelText("ID de pedido"), { target: { value: "o1" } });
    fireEvent.click(screen.getByRole("button", { name: "Consultar" }));
    await screen.findByText(/Pedido o1/);
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("fallo"));
    fireEvent.change(screen.getByLabelText("ID de pedido"), { target: { value: "o2" } });
    fireEvent.click(screen.getByRole("button", { name: "Consultar" }));
    await waitFor(() => expect(screen.queryByText(/Pedido o1/)).not.toBeInTheDocument());
  });

  it("rechaza stock negativo al editar una variante", async () => {
    sesion("admin");
    vi.spyOn(globalThis, "fetch").mockImplementation(async () => respuesta([{ id: "p1", name: "Camiseta", description: "", category: "ropa", price: 20, images: [], variants: [{ size: "M", stock: 3 }] }]));
    render(<AuthProvider><AdministracionComercio /></AuthProvider>);
    await screen.findByText("Camiseta");
    fireEvent.change(screen.getByLabelText("Nueva talla"), { target: { value: "XL" } });
    fireEvent.change(screen.getByLabelText("Nuevo stock"), { target: { value: "-1" } });
    fireEvent.click(screen.getByRole("button", { name: "Añadir variante" }));
    expect(screen.getByRole("alert")).toHaveTextContent("stock");
  });
});

describe("proveedores y portal", () => {
  it("registra una empresa solo cuando /me responde 404", async () => {
    sesion("provider");
    const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
      if (String(input).includes("providers/me")) return new Response(null, { status: 404 });
      if (init?.method === "POST") return respuesta({ id: "pr1", user_id: "u1", company_name: "Empresa", cif_nif: "B1", service_category: "Sonido", contact_email: "a@b.com" }, 201);
      return respuesta([]);
    });
    render(<AuthProvider><PortalProveedor /></AuthProvider>);
    await screen.findByRole("heading", { name: "Registrar empresa" });
    fireEvent.change(screen.getByLabelText("company_name"), { target: { value: "Empresa" } });
    fireEvent.change(screen.getByLabelText("cif_nif"), { target: { value: "B1" } });
    fireEvent.change(screen.getByLabelText("service_category"), { target: { value: "Sonido" } });
    fireEvent.change(screen.getByLabelText("contact_email"), { target: { value: "a@b.com" } });
    fireEvent.click(screen.getByRole("button", { name: "Registrar empresa" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith("/api/proveedores/providers", expect.objectContaining({ method: "POST" })));
  });

  it("muestra 403 y no ofrece el registro como si faltara la empresa", async () => {
    sesion("provider");
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => String(input).includes("providers/me") ? new Response(null, { status: 403 }) : respuesta([]));
    render(<AuthProvider><PortalProveedor /></AuthProvider>);
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("permisos"));
    expect(screen.queryByRole("button", { name: "Registrar empresa" })).not.toBeInTheDocument();
  });

  it("consulta espacios y crea una propuesta desde el portal", async () => {
    sesion("provider");
    const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
      const url = String(input);
      if (url.includes("providers/me")) return respuesta({ id: "pr1", user_id: "u1", company_name: "Empresa", cif_nif: "B1", service_category: "Sonido", contact_email: "a@b.com" });
      if (url.includes("requests/provider")) return respuesta([]);
      if (url.includes("/events")) return respuesta([{ id: "e1", name: "Festival" }]);
      if (url.includes("/spaces")) return respuesta([{ id: "s1", event_id: "e1", name: "Escenario", base_price: 10, is_available: true }]);
      if (init?.method === "POST") return respuesta({ id: "r1", provider_id: "pr1", event_id: "e1", space_id: "s1", budget_proposal: 100, status: "pending" }, 201);
      return respuesta([]);
    });
    render(<AuthProvider><PortalProveedor /></AuthProvider>);
    await screen.findByRole("heading", { name: "Empresa" });
    fireEvent.change(screen.getByLabelText("Evento"), { target: { value: "e1" } });
    await screen.findByRole("option", { name: "Escenario" });
    fireEvent.change(screen.getByLabelText("Espacio"), { target: { value: "s1" } });
    fireEvent.change(screen.getByLabelText("Presupuesto"), { target: { value: "100" } });
    fireEvent.click(screen.getByRole("button", { name: "Enviar propuesta" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith("/api/proveedores/requests", expect.objectContaining({ method: "POST" })));
  });

  it("aprueba y rechaza propuestas mediante los estados permitidos", async () => {
    sesion("admin");
    const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
      const url = String(input);
      if (init?.method === "PUT") return respuesta({ id: "r1", status: "approved" });
      if (url.includes("requests/event")) return respuesta([{ id: "r1", provider_id: "pr1", space_id: "s1", event_id: "e1", budget_proposal: 100, setup_date: null, status: "pending" }]);
      if (url.includes("/spaces")) return respuesta([]);
      if (url.includes("/events")) return respuesta([{ id: "e1", name: "Festival" }]);
      if (url.includes("external-services")) return respuesta([]);
      return respuesta([{ id: "pr1", user_id: "u1", company_name: "Empresa", cif_nif: "B1", service_category: "Sonido", contact_email: "a@b.com" }]);
    });
    vi.spyOn(window, "confirm").mockReturnValue(true);
    render(<AuthProvider><AdministracionProveedores /></AuthProvider>);
    fireEvent.change(await screen.findByLabelText("Evento"), { target: { value: "e1" } });
    await screen.findByRole("button", { name: "Aprobar" });
    fireEvent.click(screen.getByRole("button", { name: "Aprobar" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith("/api/proveedores/requests/r1/status", expect.objectContaining({ method: "PUT", body: JSON.stringify({ status: "approved" }) })));
  });
});
