
from pathlib import Path
import re

import yaml


RAIZ = Path(__file__).resolve().parent


# ============================================================
# NUEVOS ENDPOINTS
# ============================================================

RUTA_CHECKIN = """
  /tickets/validate:
    post:
      tags:
        - Pases y Entradas
      summary: Validar una entrada mediante QR
      description: >
        Valida una entrada y la marca como utilizada.
        No permite usar dos veces el mismo QR.
        Operacion exclusiva para administradores.
      operationId: validateTicket
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - qr_code
              properties:
                qr_code:
                  type: string
                  minLength: 1
                  maxLength: 200
      responses:
        '200':
          description: Entrada validada correctamente.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Ticket'
        '400':
          description: Codigo QR incorrecto.
        '401':
          description: No autenticado.
        '403':
          description: Se requiere administrador.
        '404':
          description: Entrada no encontrada.
        '409':
          description: Entrada utilizada o cancelada.
        '503':
          description: Autenticacion no disponible.
"""

RUTA_CANCELACION = """
  /orders/{id}/cancel:
    post:
      tags:
        - Pedidos
      summary: Cancelar un pedido propio pendiente
      operationId: cancelOrder
      security:
        - BearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Pedido cancelado correctamente.
        '401':
          description: No autenticado.
        '403':
          description: Pedido de otro usuario.
        '404':
          description: Pedido no encontrado.
        '409':
          description: Pedido no cancelable.
        '503':
          description: Autenticacion no disponible.
"""

RUTA_PAGO = """
  /orders/{id}/pay:
    post:
      tags:
        - Pedidos
      summary: Simular el pago de un pedido
      description: >
        Pago simulado de desarrollo.
        No realiza ningun cargo bancario real.
      operationId: payOrder
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
              type: object
              required:
                - payment_token
              properties:
                payment_token:
                  type: string
      responses:
        '200':
          description: Pago simulado correctamente.
        '400':
          description: Token de pago rechazado.
        '401':
          description: No autenticado.
        '403':
          description: Pedido de otro usuario.
        '404':
          description: Pedido no encontrado.
        '409':
          description: Pedido no pagable.
        '422':
          description: Datos incompletos.
        '503':
          description: Autenticacion no disponible.
"""

RUTA_RESET_CONFIRM = """
  /auth/reset-password/confirm:
    post:
      tags:
        - Autenticación
      summary: Confirmar recuperacion de contrasena
      description: >
        Confirma el restablecimiento mediante un token
        temporal enviado por correo electronico.
      operationId: confirmPasswordReset
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - token
                - new_password
              properties:
                token:
                  type: string
                  minLength: 1
                new_password:
                  type: string
                  minLength: 8
      responses:
        '200':
          description: Contrasena actualizada correctamente.
        '400':
          description: Token invalido, caducado o utilizado.
"""


# ============================================================
# MODIFICACIONES DE CONTRATOS
# ============================================================

def agregar_ruta(texto, ruta, definicion):
    """
    Introduce una ruta antes de components,
    siempre que todavia no exista.
    """

    if re.search(
        rf"(?m)^  {re.escape(ruta)}:\s*$",
        texto
    ):
        return texto

    marcador = "\ncomponents:\n"

    if marcador not in texto:
        raise RuntimeError(
            f"No se encuentra components para {ruta}"
        )

    return texto.replace(
        marcador,
        "\n" + definicion.strip("\n")
        + "\n\ncomponents:\n",
        1
    )


def agregar_idempotencia(texto):
    """
    Documenta la cabecera opcional
    Idempotency-Key en POST /orders.
    """

    if "name: Idempotency-Key" in texto:
        return texto

    marcador = "      operationId: createOrder\n"

    if texto.count(marcador) != 1:
        raise RuntimeError(
            "No se encuentra createOrder en OpenAPI"
        )

    cabecera = """      parameters:
        - name: Idempotency-Key
          in: header
          required: false
          description: >
            Identifica reintentos de una misma compra.
            La misma clave y compra devuelve el pedido original.
          schema:
            type: string
            minLength: 1
            maxLength: 128
"""

    return texto.replace(
        marcador,
        marcador + cabecera,
        1
    )


def agregar_respuesta_429(texto):
    """
    Documenta el bloqueo temporal del login
    tras cinco intentos incorrectos.
    """

    inicio = texto.find("  /auth/login:\n")

    if inicio == -1:
        raise RuntimeError(
            "No se encuentra /auth/login"
        )

    siguiente = texto.find(
        "\n  /",
        inicio + 1
    )

    if siguiente == -1:
        siguiente = texto.find(
            "\ncomponents:",
            inicio
        )

    bloque = texto[inicio:siguiente]

    if re.search(r"""['"]429['"]:""", bloque):
        return texto

    patron = (
        r"""(?m)^(        ['"]401['"]:\n"""
        r"""          description: [^\n]+\n)"""
    )

    coincidencia = re.search(
        patron,
        bloque
    )

    if coincidencia is None:
        raise RuntimeError(
            "No se encuentra respuesta 401 del login"
        )

    nueva_respuesta = """        '429':
          description: Demasiados intentos de inicio de sesion.
          headers:
            Retry-After:
              description: Segundos restantes del bloqueo.
              schema:
                type: integer
"""

    bloque_nuevo = (
        bloque[:coincidencia.end()]
        + nueva_respuesta
        + bloque[coincidencia.end():]
    )

    return (
        texto[:inicio]
        + bloque_nuevo
        + texto[siguiente:]
    )


def actualizar_eventos(texto):
    return agregar_ruta(
        texto,
        "/tickets/validate",
        RUTA_CHECKIN
    )


def actualizar_comercio(texto):
    texto = agregar_idempotencia(texto)

    texto = agregar_ruta(
        texto,
        "/orders/{id}/cancel",
        RUTA_CANCELACION
    )

    texto = agregar_ruta(
        texto,
        "/orders/{id}/pay",
        RUTA_PAGO
    )

    return texto


def actualizar_auth(texto):
    texto = agregar_ruta(
        texto,
        "/auth/reset-password/confirm",
        RUTA_RESET_CONFIRM
    )

    return agregar_respuesta_429(texto)


# ============================================================
# VALIDACION
# ============================================================

def comprobar_contrato(texto, servicio):

    contrato = yaml.safe_load(texto)

    assert contrato["openapi"].startswith("3.")
    assert isinstance(contrato["paths"], dict)

    rutas = contrato["paths"]

    if servicio == "events":
        assert "post" in rutas["/tickets/validate"]

    elif servicio == "commerce":

        assert "post" in rutas["/orders/{id}/cancel"]
        assert "post" in rutas["/orders/{id}/pay"]

        parametros = rutas["/orders"]["post"][
            "parameters"
        ]

        assert any(
            parametro["name"] == "Idempotency-Key"
            for parametro in parametros
        )

    elif servicio == "auth":

        assert (
            "post"
            in rutas["/auth/reset-password/confirm"]
        )

        respuestas = rutas["/auth/login"][
            "post"
        ]["responses"]

        assert "429" in respuestas


# ============================================================
# EJECUCION
# ============================================================

def main():

    archivos = [
        (
            "event-service/openapi.yaml",
            "events",
            actualizar_eventos
        ),
        (
            "event-service/generated/openapi.yaml",
            "events",
            actualizar_eventos
        ),
        (
            "commerce-service/openapi.yaml",
            "commerce",
            actualizar_comercio
        ),
        (
            "commerce-service/generated/openapi.yaml",
            "commerce",
            actualizar_comercio
        ),
        (
            "auth-service/openapi.yaml",
            "auth",
            actualizar_auth
        ),
        (
            "auth-service/generated/openapi.yaml",
            "auth",
            actualizar_auth
        )
    ]

    cambios = []

    # Validar todos antes de escribir ninguno.
    for ruta, servicio, funcion in archivos:

        archivo = RAIZ / ruta

        original = archivo.read_text(
            encoding="utf-8"
        )

        actualizado = funcion(original)

        comprobar_contrato(
            actualizado,
            servicio
        )

        cambios.append(
            (archivo, original, actualizado)
        )

    # Guardar solo los archivos modificados.
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
        "\nContratos OpenAPI sincronizados correctamente."
    )


if __name__ == "__main__":
    main()
