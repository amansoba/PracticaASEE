import { expect, test, type Page } from "@playwright/test";

const adminConfigured = Boolean(process.env.E2E_ADMIN_EMAIL && process.env.E2E_ADMIN_PASSWORD);
const providerConfigured = Boolean(process.env.E2E_PROVIDER_EMAIL && process.env.E2E_PROVIDER_PASSWORD);
const catalogPath = process.env.E2E_ADMIN_CATALOG_PATH ?? "/admin/catalogo";
const commercePath = process.env.E2E_ADMIN_COMMERCE_PATH ?? "/admin/comercio";
const providersPath = process.env.E2E_ADMIN_PROVIDERS_PATH ?? "/admin/proveedores";
const providerPath = process.env.E2E_PROVIDER_PATH ?? "/portal/proveedor";

async function iniciarSesion(page: Page, email: string, password: string) {
  await page.goto("/login");
  await page.getByLabel("Correo electrónico").fill(email);
  await page.getByLabel("Contraseña").fill(password);
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page).toHaveURL(/\/$/);
}

test.describe("flujos E2E de administrador", () => {
  test.skip(!adminConfigured, "Configura E2E_ADMIN_EMAIL y E2E_ADMIN_PASSWORD; además Álvaro debe integrar las rutas.");
  test("gestiona artistas, productos y propuestas con acciones reales", async ({ page }) => {
    test.slow();
    await iniciarSesion(page, process.env.E2E_ADMIN_EMAIL!, process.env.E2E_ADMIN_PASSWORD!);

    await page.goto(catalogPath);
    const nombre = `Artista E2E ${Date.now()}`;
    await page.getByLabel("Nombre").fill(nombre);
    await page.getByLabel("Género").fill("E2E");
    await page.getByRole("button", { name: "Crear artista" }).click();
    await expect(page.getByRole("status")).toContainText("creado");
    await page.getByLabel("Buscar por nombre").fill(nombre);
    await expect(page.getByText(nombre)).toBeVisible();
    await page.getByRole("button", { name: "Editar" }).click();
    await page.getByLabel("Nombre").fill(`${nombre} editado`);
    await page.getByRole("button", { name: "Guardar cambios" }).click();
    await expect(page.getByRole("status")).toContainText("actualizado");
    page.once("dialog", (dialog) => void dialog.accept());
    await page.getByRole("button", { name: "Eliminar" }).click();
    await expect(page.getByRole("status")).toContainText("eliminado");

    await page.goto(commercePath);
    await page.getByLabel("Nombre").fill(`Producto E2E ${Date.now()}`);
    await page.getByLabel("Categoría").fill("e2e");
    await page.getByLabel("Precio").fill("12.50");
    await page.getByLabel("Nueva talla").fill("M");
    await page.getByLabel("Nuevo stock").fill("5");
    await page.getByRole("button", { name: "Añadir variante" }).click();
    await page.getByRole("button", { name: "Guardar producto" }).click();
    await expect(page.getByRole("status")).toContainText("creado");

    await page.goto(providersPath);
    const evento = page.getByLabel("Evento");
    if (await evento.locator("option").count() > 1) {
      await evento.selectOption({ index: 1 });
      const aprobar = page.getByRole("button", { name: "Aprobar" }).first();
      const rechazar = page.getByRole("button", { name: "Rechazar" }).first();
      if (await aprobar.isVisible()) {
        page.once("dialog", (dialog) => void dialog.accept());
        await aprobar.click();
      } else if (await rechazar.isVisible()) {
        page.once("dialog", (dialog) => void dialog.accept());
        await rechazar.click();
      }
    }
  });
});

test.describe("flujos E2E de proveedor", () => {
  test.skip(!providerConfigured, "Configura E2E_PROVIDER_EMAIL y E2E_PROVIDER_PASSWORD; además Álvaro debe integrar la ruta.");
  test("registra empresa si procede y envía una propuesta real", async ({ page }) => {
    test.slow();
    await iniciarSesion(page, process.env.E2E_PROVIDER_EMAIL!, process.env.E2E_PROVIDER_PASSWORD!);
    await page.goto(providerPath);

    const registrar = page.getByRole("button", { name: "Registrar empresa" });
    if (await registrar.isVisible()) {
      await page.getByLabel("company_name").fill(`Proveedor E2E ${Date.now()}`);
      await page.getByLabel("cif_nif").fill(`B${Date.now().toString().slice(-8)}`);
      await page.getByLabel("service_category").fill("Sonido");
      await page.getByLabel("contact_email").fill(process.env.E2E_PROVIDER_EMAIL!);
      await registrar.click();
      await expect(page.getByRole("status")).toContainText("registrada");
    }

    const evento = page.getByLabel("Evento");
    await evento.selectOption({ index: 1 });
    const espacio = page.getByLabel("Espacio");
    await expect(espacio.locator("option").nth(1)).toBeVisible();
    await espacio.selectOption({ index: 1 });
    await page.getByLabel("Presupuesto").fill("100");
    await page.getByRole("button", { name: "Enviar propuesta" }).click();
    await expect(page.getByRole("status")).toContainText("enviada");
  });
});
