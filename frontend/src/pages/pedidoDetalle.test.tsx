import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthProvider } from "../context/AuthContext";
import PedidoDetalle from "./PedidoDetalle";

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
  status: "pending",
  created_at: "2026-11-16T12:00:00Z",
};

function respuesta(datos: unknown, status = 200) {
  return new Response(JSON.stringify(datos), {
    status,
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
      id: "u1",
      name: "Cliente",
      email: "client@example.com",
      role: "client",
      phone: null,
      avatar_url: null,
    })
  );
});

describe("cancelación de pedido del cliente", () => {
  it("invoca POST /orders/{id}/cancel y actualiza el estado en pantalla", async () => {
    let estado = "pending";

    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockImplementation(async (input, init) => {
        const url = String(input);

        if (url === "/api/tienda/orders/o1/cancel" && init?.method === "POST") {
          estado = "cancelled";
          return respuesta({ ...pedido, status: estado });
        }

        if (url === "/api/tienda/orders/o1") {
          return respuesta({ ...pedido, status: estado });
        }

        return respuesta([]);
      });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={["/mis-pedidos/o1"]}>
          <Routes>
            <Route path="/mis-pedidos/:id" element={<PedidoDetalle />} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    const boton = await screen.findByRole("button", {
      name: "Cancelar pedido",
    });

    fireEvent.click(boton);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/tienda/orders/o1/cancel",
        expect.objectContaining({ method: "POST" })
      );
    });

    await waitFor(() => {
      expect(screen.getByText("cancelled")).toBeInTheDocument();
    });
  });
});
