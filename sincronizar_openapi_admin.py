
from pathlib import Path
import re

import yaml


RAIZ = Path(__file__).resolve().parent


# ============================================================
# RUTAS DE CATALOGO
# ============================================================

CANCIONES = """
  /artists/{artistId}/songs/{songId}:
    put:
      tags:
        - Canciones
      summary: Actualizar una cancion
      operationId: updateSong
      security:
        - BearerAuth: []
      parameters:
        - name: artistId
          in: path
          required: true
          schema:
            type: string
        - name: songId
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateSongRequest'
      responses:
        '200':
          description: Cancion actualizada.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Song'
        '400':
          description: Datos invalidos.
        '401':
          description: No autenticado.
        '403':
          description: Se requiere administrador.
        '404':
          description: Artista o cancion no encontrados.
        '503':
          description: Autenticacion no disponible.
    delete:
      tags:
        - Canciones
      summary: Eliminar una cancion
      operationId: deleteSong
      security:
        - BearerAuth: []
      parameters:
        - name: artistId
          in: path
          required: true
          schema:
            type: string
        - name: songId
          in: path
          required: true
          schema:
            type: string
      responses:
        '204':
          description: Cancion eliminada.
        '401':
          description: No autenticado.
        '403':
          description: Se requiere administrador.
        '404':
          description: Artista o cancion no encontrados.
        '503':
          description: Autenticacion no disponible.
"""


# ============================================================
# RUTAS DE PROVEEDORES
# ============================================================

SERVICIOS = """
  /external-services/{id}:
    put:
      tags:
        - Servicios y Espacios
      summary: Actualizar servicio externo
      operationId: updateExternalService
      security:
        - BearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateExternalServiceRequest'
      responses:
        '200':
          description: Servicio actualizado.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ExternalService'
        '400':
          description: Datos invalidos.
        '401':
          description: No autenticado.
        '403':
          description: Se requiere administrador.
        '404':
          description: Servicio no encontrado.
        '503':
          description: Autenticacion no disponible.
    delete:
      tags:
        - Servicios y Espacios
      summary: Eliminar servicio externo
      operationId: deleteExternalService
      security:
        - BearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '204':
          description: Servicio eliminado.
        '401':
          description: No autenticado.
        '403':
          description: Se requiere administrador.
        '404':
          description: Servicio no encontrado.
        '503':
          description: Autenticacion no disponible.
"""

ESPACIOS = """
  /spaces/{id}:
    put:
      tags:
        - Servicios y Espacios
      summary: Actualizar un espacio alquilable
      operationId: updateSpace
      security:
        - BearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateSpaceRequest'
      responses:
        '200':
          description: Espacio actualizado.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Space'
        '400':
          description: Datos invalidos.
        '401':
          description: No autenticado.
        '403':
          description: Se requiere administrador.
        '404':
          description: Espacio o evento no encontrado.
        '409':
          description: Conflicto con espacios o propuestas.
        '503':
          description: Servicio externo no disponible.
    delete:
      tags:
        - Servicios y Espacios
      summary: Eliminar un espacio
      operationId: deleteSpace
      security:
        - BearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '204':
          description: Espacio eliminado.
        '401':
          description: No autenticado.
        '403':
          description: Se requiere administrador.
        '404':
          description: Espacio no encontrado.
        '409':
          description: El espacio tiene propuestas.
        '503':
          description: Autenticacion no disponible.
"""


# ============================================================
# LISTADO GLOBAL DE PEDIDOS
# ============================================================

LISTAR_PEDIDOS = """
    get:
      tags:
        - Pedidos
      summary: Consultar todos los pedidos
      description: >
        Devuelve todos los pedidos registrados.
        Operacion exclusiva para administradores.
      operationId: listAllOrders
      security:
        - BearerAuth: []
      responses:
        '200':
          description: Listado global de pedidos.
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Order'
        '401':
          description: No autenticado.
        '403':
          description: Se requiere administrador.
        '503':
          description: Autenticacion no disponible.
"""


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def agregar_ruta(texto, ruta, contenido):

    if re.search(
        rf"(?m)^  {re.escape(ruta)}:\s*$",
        texto
    ):
        return texto

    marcador = "\ncomponents:\n"

    if marcador not in texto:
        raise RuntimeError(
            f"No se encuentra components en {ruta}"
        )

    return texto.replace(
        marcador,
        "\n" + contenido.strip("\n")
        + "\n\ncomponents:\n",
        1
    )


def agregar_get_pedidos(texto):

    marcador = "  /orders:\n"

    if marcador not in texto:
        raise RuntimeError(
            "No se encuentra /orders"
        )

    inicio = texto.index(marcador)
    contenido_inicio = inicio + len(marcador)

    siguiente = re.search(
        r"(?m)^  /[^\n]+:\s*$",
        texto[contenido_inicio:]
    )

    if siguiente is None:
        raise RuntimeError(
            "No se encuentra el final de /orders"
        )

    fin = contenido_inicio + siguiente.start()

    bloque = texto[inicio:fin]

    if re.search(r"(?m)^    get:\s*$", bloque):
        return texto

    return (
        texto[:fin]
        + LISTAR_PEDIDOS.strip("\n")
        + "\n"
        + texto[fin:]
    )


def actualizar_catalogo(texto):

    return agregar_ruta(
        texto,
        "/artists/{artistId}/songs/{songId}",
        CANCIONES
    )


def actualizar_proveedores(texto):

    texto = agregar_ruta(
        texto,
        "/external-services/{id}",
        SERVICIOS
    )

    return agregar_ruta(
        texto,
        "/spaces/{id}",
        ESPACIOS
    )


def actualizar_comercio(texto):

    return agregar_get_pedidos(texto)


# ============================================================
# COMPROBACION
# ============================================================

def comprobar(texto, servicio):

    contrato = yaml.safe_load(texto)
    rutas = contrato["paths"]

    if servicio == "catalogo":
        ruta = rutas[
            "/artists/{artistId}/songs/{songId}"
        ]
        assert "put" in ruta
        assert "delete" in ruta

    elif servicio == "proveedores":
        for nombre in (
            "/external-services/{id}",
            "/spaces/{id}"
        ):
            assert "put" in rutas[nombre]
            assert "delete" in rutas[nombre]

    elif servicio == "comercio":
        assert "post" in rutas["/orders"]
        assert "get" in rutas["/orders"]


def main():

    archivos = [
        (
            "catalog-service/openapi.yaml",
            "catalogo",
            actualizar_catalogo
        ),
        (
            "catalog-service/generated/openapi.yaml",
            "catalogo",
            actualizar_catalogo
        ),
        (
            "provider-service/openapi.yaml",
            "proveedores",
            actualizar_proveedores
        ),
        (
            "provider-service/generated/openapi.yaml",
            "proveedores",
            actualizar_proveedores
        ),
        (
            "commerce-service/openapi.yaml",
            "comercio",
            actualizar_comercio
        ),
        (
            "commerce-service/generated/openapi.yaml",
            "comercio",
            actualizar_comercio
        )
    ]

    cambios = []

    for ruta, servicio, funcion in archivos:

        archivo = RAIZ / ruta

        original = archivo.read_text(
            encoding="utf-8"
        )

        actualizado = funcion(original)

        comprobar(actualizado, servicio)

        cambios.append(
            (archivo, original, actualizado)
        )

    for archivo, original, actualizado in cambios:

        if original == actualizado:
            print(
                f"OK sin cambios: {archivo.relative_to(RAIZ)}"
            )
            continue

        archivo.write_text(
            actualizado,
            encoding="utf-8"
        )

        print(
            f"OK actualizado: {archivo.relative_to(RAIZ)}"
        )

    print(
        "\nContratos administrativos sincronizados."
    )


if __name__ == "__main__":
    main()
