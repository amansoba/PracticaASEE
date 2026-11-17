import { afterEach, describe, expect, it, vi } from "vitest";
import { crearCancion, obtenerCanciones } from "./catalogoAdmin";
import { actualizarEstadoPedido, actualizarProducto, crearProducto } from "./comercioAdmin";
import { actualizarEstadoPropuesta, crearProveedor, crearPropuesta, obtenerMisPropuestas } from "./proveedoresAdmin";
import { actualizarArtista, crearArtista, eliminarArtista, obtenerArtistas } from "./artistas";
import { obtenerMiEmpresa, ProveedorApiError } from "./proveedores";

afterEach(() => vi.restoreAllMocks());
const ok = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

describe("servicios de catálogo", () => {
  it("lista canciones por artista y crea una canción autenticada", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(ok([{ id: "s1", artist_id: "a1", title: "Tema" }])).mockResolvedValueOnce(ok({ id: "s2", artist_id: "a1", title: "Nuevo" }, 201));
    await expect(obtenerCanciones("a1")).resolves.toHaveLength(1);
    await crearCancion("a1", { title: "Nuevo" }, "token");
    expect(fetchMock.mock.calls[1][1]).toMatchObject({ method: "POST" });
    expect(new Headers((fetchMock.mock.calls[1][1] as RequestInit).headers).get("Authorization")).toBe("Bearer token");
  });

  it("filtra artistas por nombre y género y conserva las operaciones CRUD", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation(async (_input, init) => {
      if (init?.method === "POST") return ok({ id: "a2", name: "Nueva", genre: "Rock" }, 201);
      if (init?.method === "PUT") return ok({ id: "a2", name: "Editada", genre: "Rock" });
      if (init?.method === "DELETE") return new Response(null, { status: 204 });
      return ok([{ id: "a1", name: "Daft Punk", genre: "Electrónica", biography: null, image_url: null }]);
    });
    await obtenerArtistas({ search: "Daft", genre: "Electrónica" });
    await crearArtista({ name: "Nueva", genre: "Rock" }, "token");
    await actualizarArtista("a2", { name: "Editada", genre: "Rock" }, "token");
    await eliminarArtista("a2", "token");
    expect(String(fetchMock.mock.calls[0][0])).toContain("search=Daft");
    expect(String(fetchMock.mock.calls[0][0])).toContain("genre=Electr%C3%B3nica");
    expect(fetchMock).toHaveBeenCalledTimes(4);
  });
});

describe("servicios de comercio y proveedores", () => {
  it("envía producto con variantes y stock al contrato", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(ok({ id: "p1" }, 201));
    await crearProducto({ name: "Camiseta", category: "ropa", price: 20, variants: [{ size: "M", stock: 4 }] }, "token");
    expect(JSON.parse(String((fetchMock.mock.calls[0][1] as RequestInit).body))).toMatchObject({ variants: [{ size: "M", stock: 4 }] });
  });
  it("usa los estados del contrato para pedidos, propuestas y proveedores", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation(async () => ok({ id: "x" }));
    await actualizarEstadoPedido("o1", "shipped", "token");
    await actualizarEstadoPropuesta("r1", "approved", "token");
    await actualizarEstadoPropuesta("r1", "rejected", "token");
    await crearProveedor({ user_id: "u1", company_name: "Empresa", cif_nif: "B1", service_category: "Sonido", contact_email: "a@b.com" }, "token");
    expect(fetchMock).toHaveBeenCalledTimes(4);
    expect(String(fetchMock.mock.calls[1][0])).toContain("/requests/r1/status");
  });

  it("actualiza productos, crea propuestas y consulta solo propuestas propias", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation(async () => ok({ id: "x", status: "pending" }));
    await actualizarProducto("p1", { name: "Camiseta", category: "ropa", price: 21, variants: [{ size: "M", stock: 5 }] }, "token");
    await crearPropuesta({ space_id: "s1", provider_id: "pr1", event_id: "e1", budget_proposal: 100 }, "token");
    await obtenerMisPropuestas("pr1", "token");
    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(String(fetchMock.mock.calls[1][0])).toContain("/requests");
    expect(String(fetchMock.mock.calls[2][0])).toContain("/requests/provider/pr1");
  });

  it.each([401, 403, 500, 503])("distingue el error HTTP %s al consultar la empresa", async (status) => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(null, { status }));
    await expect(obtenerMiEmpresa("token")).rejects.toMatchObject({ status });
    await expect(obtenerMiEmpresa("token")).rejects.toBeInstanceOf(ProveedorApiError);
  });
});
