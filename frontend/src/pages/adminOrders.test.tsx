
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthProvider } from "../context/AuthContext";
import AdministracionComercio from "./AdministracionComercio";

const pedido = {
  id: "o1",
  user_id: "u1",
  items: [
    {
      product_id: "p1",
      size: "M",
      quantity: 1,
      unit_price: 10,
    },
  ],
  total_price: 10,
  status: "paid",
  created_at: "2026-11-16T12:00:00Z",
};

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
      name: "Administrador",
      email: "admin@example.com",
      role: "admin",
      phone: null,
      avatar_url: null,
    })
  );
});

describe("listado administrativo de pedidos", () => {
  it("lista los pedidos y permite seleccionar su detalle", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch")
      .mockImplementation(async (input) => {
        const url = String(input);

        if (url === "/api/tienda/orders") {
          return respuesta([pedido]);
        }

        return respuesta([]);
      });

    render(
      <AuthProvider>
        <AdministracionComercio />
      </AuthProvider>
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Cargar pedidos",
      })
    );

    await screen.findByRole("button", {
      name: "Ver pedido o1",
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/tienda/orders",
      expect.objectContaining({
        headers: expect.any(Headers),
      })
    );

    const llamada = fetchMock.mock.calls.find(
      ([url]) => String(url) === "/api/tienda/orders"
    );

    expect(
      new Headers(llamada?.[1]?.headers).get("Authorization")
    ).toBe("Bearer test-token");

    fireEvent.click(
      screen.getByRole("button", {
        name: "Ver pedido o1",
      })
    );

    expect(
      screen.getByLabelText("ID de pedido")
    ).toHaveValue("o1");

    expect(
      screen.getByLabelText("Estado del pedido")
    ).toHaveValue("paid");
  });

  it("actualiza el listado tras cambiar el estado", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch")
      .mockImplementation(async (input, init) => {
        const url = String(input);

        if (
          url === "/api/tienda/orders/o1/status" &&
          init?.method === "PUT"
        ) {
          return respuesta({
            ...pedido,
            status: "shipped",
          });
        }

        if (url === "/api/tienda/orders") {
          return respuesta([pedido]);
        }

        return respuesta([]);
      });

    render(
      <AuthProvider>
        <AdministracionComercio />
      </AuthProvider>
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Cargar pedidos",
      })
    );

    fireEvent.click(
      await screen.findByRole("button", {
        name: "Ver pedido o1",
      })
    );

    fireEvent.change(
      screen.getByLabelText("Estado del pedido"),
      { target: { value: "shipped" } }
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Actualizar estado",
      })
    );

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/tienda/orders/o1/status",
        expect.objectContaining({
          method: "PUT",
          body: JSON.stringify({ status: "shipped" }),
        })
      );

      expect(
        screen.getByText("Estado: shipped")
      ).toBeInTheDocument();
    });
  });
});
