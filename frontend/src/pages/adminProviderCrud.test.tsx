
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthProvider } from "../context/AuthContext";
import AdministracionProveedores from "./AdministracionProveedores";

function respuesta(datos: unknown) {
  return new Response(JSON.stringify(datos), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

beforeEach(() => {
  sessionStorage.clear();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();

  sessionStorage.setItem("subsonic_token", "test-token");
  sessionStorage.setItem(
    "subsonic_usuario",
    JSON.stringify({
      id: "admin1",
      name: "Admin",
      email: "admin@example.com",
      role: "admin",
      phone: null,
      avatar_url: null,
    })
  );
});

describe("CRUD administrativo de servicios y espacios", () => {
  it("edita y elimina servicios", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch")
      .mockImplementation(async (input, init) => {
        const url = String(input);

        if (
          url.endsWith("/external-services/s1") &&
          init?.method === "PUT"
        ) {
          return respuesta({
            id: "s1",
            name: "Sonido premium",
            description: "Actualizado",
          });
        }

        if (
          url.endsWith("/external-services/s1") &&
          init?.method === "DELETE"
        ) {
          return new Response(null, { status: 204 });
        }

        if (url.endsWith("/external-services")) {
          return respuesta([
            {
              id: "s1",
              name: "Sonido",
              description: "Inicial",
            },
          ]);
        }

        return respuesta([]);
      });

    vi.spyOn(window, "confirm").mockReturnValue(true);

    render(
      <AuthProvider>
        <AdministracionProveedores />
      </AuthProvider>
    );

    fireEvent.click(
      await screen.findByRole("button", {
        name: "Editar servicio",
      })
    );

    fireEvent.change(
      screen.getByLabelText("Nombre del servicio"),
      { target: { value: "Sonido premium" } }
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Guardar servicio",
      })
    );

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/proveedores/external-services/s1",
        expect.objectContaining({ method: "PUT" })
      );
    });

    expect(
      await screen.findByText("Sonido premium: Actualizado")
    ).toBeInTheDocument();

    fireEvent.click(
      screen.getByRole("button", {
        name: "Eliminar servicio",
      })
    );

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/proveedores/external-services/s1",
        expect.objectContaining({ method: "DELETE" })
      );
      expect(
        screen.queryByText("Sonido premium: Actualizado")
      ).not.toBeInTheDocument();
    });
  });

  it("edita y elimina espacios de un evento", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch")
      .mockImplementation(async (input, init) => {
        const url = String(input);

        if (
          url.endsWith("/spaces/sp1") &&
          init?.method === "PUT"
        ) {
          return respuesta({
            id: "sp1",
            event_id: "e1",
            name: "Escenario VIP",
            dimensions: "20x20",
            base_price: 200,
            is_available: false,
          });
        }

        if (
          url.endsWith("/spaces/sp1") &&
          init?.method === "DELETE"
        ) {
          return new Response(null, { status: 204 });
        }

        if (url.includes("/spaces?event_id=e1")) {
          return respuesta([
            {
              id: "sp1",
              event_id: "e1",
              name: "Escenario",
              dimensions: "10x10",
              base_price: 100,
              is_available: true,
            },
          ]);
        }

        if (url.endsWith("/events")) {
          return respuesta([{ id: "e1", name: "Festival" }]);
        }

        return respuesta([]);
      });

    vi.spyOn(window, "confirm").mockReturnValue(true);

    render(
      <AuthProvider>
        <AdministracionProveedores />
      </AuthProvider>
    );

    fireEvent.change(
      await screen.findByLabelText("Evento"),
      { target: { value: "e1" } }
    );

    fireEvent.click(
      await screen.findByRole("button", {
        name: "Editar espacio",
      })
    );

    fireEvent.change(
      screen.getByLabelText("Nombre del espacio"),
      { target: { value: "Escenario VIP" } }
    );

    fireEvent.change(
      screen.getByLabelText("Precio base del espacio"),
      { target: { value: "200" } }
    );

    fireEvent.click(
      screen.getByLabelText("Disponible")
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Guardar espacio",
      })
    );

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/proveedores/spaces/sp1",
        expect.objectContaining({
          method: "PUT",
          body: expect.stringContaining("Escenario VIP"),
        })
      );
    });

    expect(
      await screen.findByText(/Escenario VIP · 200.00 €/)
    ).toBeInTheDocument();

    fireEvent.click(
      screen.getByRole("button", {
        name: "Eliminar espacio",
      })
    );

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/proveedores/spaces/sp1",
        expect.objectContaining({ method: "DELETE" })
      );
      expect(
        screen.queryByText(/Escenario VIP · 200.00 €/)
      ).not.toBeInTheDocument();
    });
  });
});
