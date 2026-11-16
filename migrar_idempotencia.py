
from pathlib import Path
import sys

from sqlalchemy import text


RAIZ = Path(__file__).resolve().parent

CARPETA_SRC = (
    RAIZ
    / "commerce-service"
    / "generated"
    / "src"
)

sys.path.insert(
    0,
    str(CARPETA_SRC)
)

from openapi_server.database import engine


def main():

    with engine.begin() as conexion:

        nombre_bd = conexion.execute(
            text("SELECT current_database()")
        ).scalar_one()

        print(
            f"Base de datos conectada: {nombre_bd}"
        )

        # Evitar cambios en otras bases de datos.
        if nombre_bd != "subsonic_commerce":
            raise RuntimeError(
                "Migracion cancelada: se esperaba "
                "la base de datos subsonic_commerce"
            )

        existe_tabla = conexion.execute(
            text("SELECT to_regclass('orders')")
        ).scalar_one()

        if existe_tabla is None:
            raise RuntimeError(
                "No existe la tabla orders. "
                "Inicializa Comercio antes de migrar."
            )

        # Agregar la clave opcional de idempotencia.
        conexion.execute(
            text(
                "ALTER TABLE orders "
                "ADD COLUMN IF NOT EXISTS "
                "idempotency_key VARCHAR(128)"
            )
        )

        # Agregar la huella de la compra original.
        conexion.execute(
            text(
                "ALTER TABLE orders "
                "ADD COLUMN IF NOT EXISTS "
                "request_fingerprint VARCHAR(64)"
            )
        )

        # Un usuario no puede registrar dos pedidos
        # con la misma clave de idempotencia.
        conexion.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS "
                "uq_orders_user_idempotency_key "
                "ON orders (user_id, idempotency_key)"
            )
        )

    print(
        "Migracion de idempotencia completada."
    )
    print(
        "Los pedidos anteriores se han conservado."
    )


if __name__ == "__main__":
    main()
