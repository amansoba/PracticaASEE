
import {
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";
import { AuthProvider } from "../context/AuthContext";
import AdministracionCatalogo from "./AdministracionCatalogo";

const artista = {
  id: "a1",
  name: "Artista",
  genre: "Rock",
  biography: null,
  image_url: null,
};

const cancion = {
  id: "s1",
  artist_id: "a1",
  title: "Tema original",
  spotify_id: null,
  spotify_url: null,
  preview_url: null,
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
      name: "Admin",
      email: "admin@example.com",
      role: "admin",
      phone: null,
      avatar_url: null,
    })
  );
});

describe("administración de canciones", () => {
  it("permite editar una canción existente", async () => {
    let canciones = [cancion];

    const fetchMock = vi.spyOn(globalThis, "fetch")
      .mockImplementation(async (input, init) => {
        const url = String(input);

        if (
          url === "/api/catalogo/artists/a1/songs/s1" &&
          init?.method === "PUT"
        ) {
          const datos = JSON.parse(String(init.body));
          canciones = [{ ...cancion, ...datos }];
          return respuesta(canciones[0]);
        }

        if (url === "/api/catalogo/artists/a1/songs") {
          return respuesta(canciones);
        }

        return respuesta([artista]);
      });

    render(
      <AuthProvider>
        <AdministracionCatalogo />
      </AuthProvider>
    );

    await screen.findByText("Artista");

    fireEvent.click(
      screen.getByRole("button", { name: "Canciones" })
    );

    await screen.findByText("Tema original");

    fireEvent.click(
      screen.getByRole("button", { name: "Editar canción" })
    );

    fireEvent.change(screen.getByLabelText("Título"), {
      target: { value: "Tema actualizado" },
    });

    fireEvent.click(
      screen.getByRole("button", { name: "Guardar canción" })
    );

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/catalogo/artists/a1/songs/s1",
        expect.objectContaining({
          method: "PUT",
          body: expect.stringContaining("Tema actualizado"),
        })
      );
    });

    expect(
      await screen.findByText("Tema actualizado")
    ).toBeInTheDocument();
  });

  it("permite eliminar una canción con confirmación", async () => {
    let canciones = [cancion];

    const fetchMock = vi.spyOn(globalThis, "fetch")
      .mockImplementation(async (input, init) => {
        const url = String(input);

        if (
          url === "/api/catalogo/artists/a1/songs/s1" &&
          init?.method === "DELETE"
        ) {
          canciones = [];
          return new Response(null, { status: 204 });
        }

        if (url === "/api/catalogo/artists/a1/songs") {
          return respuesta(canciones);
        }

        return respuesta([artista]);
      });

    vi.spyOn(window, "confirm").mockReturnValue(true);

    render(
      <AuthProvider>
        <AdministracionCatalogo />
      </AuthProvider>
    );

    await screen.findByText("Artista");

    fireEvent.click(
      screen.getByRole("button", { name: "Canciones" })
    );

    await screen.findByText("Tema original");

    fireEvent.click(
      screen.getByRole("button", { name: "Eliminar canción" })
    );

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/catalogo/artists/a1/songs/s1",
        expect.objectContaining({ method: "DELETE" })
      );
    });

    expect(
      await screen.findByText("No hay canciones para este artista.")
    ).toBeInTheDocument();
  });
});
