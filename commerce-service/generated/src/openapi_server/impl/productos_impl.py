
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from openapi_server.apis.productos_api_base import (
    BaseProductosApi
)
from openapi_server.models.create_product_request import (
    CreateProductRequest
)
from openapi_server.models.product import Product
from openapi_server.models.product_variant import ProductVariant

from openapi_server.database import SessionLocal
from openapi_server.db_models import (
    ProductDB,
    ProductVariantDB,
    OrderDB,
    OrderItemDB
)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def convertir_producto(producto: ProductDB) -> Product:
    return Product(
        id=producto.id,
        name=producto.name,
        description=producto.description,
        category=producto.category,
        price=float(producto.price),
        images=producto.images,
        variants=[
            ProductVariant(
                size=variante.size,
                stock=variante.stock
            )
            for variante in sorted(
                producto.variants,
                key=lambda variante: variante.size
            )
        ]
    )


def validar_producto(
    solicitud: CreateProductRequest
) -> dict:

    nombre = solicitud.name.strip()
    categoria = solicitud.category.strip()

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre del producto es obligatorio"
        )

    if not categoria:
        raise HTTPException(
            status_code=400,
            detail="La categoria del producto es obligatoria"
        )

    try:
        precio = Decimal(str(solicitud.price))
    except (InvalidOperation, ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Precio no valido"
        )

    if not precio.is_finite() or precio < 0:
        raise HTTPException(
            status_code=400,
            detail="El precio debe ser mayor o igual que cero"
        )

    if precio.as_tuple().exponent < -2:
        raise HTTPException(
            status_code=400,
            detail="El precio admite como maximo dos decimales"
        )

    variantes = []
    tallas_utilizadas = set()

    for variante in solicitud.variants or []:
        talla = variante.size.strip()

        if not talla:
            raise HTTPException(
                status_code=400,
                detail="La talla no puede estar vacia"
            )

        if talla in tallas_utilizadas:
            raise HTTPException(
                status_code=400,
                detail="No se puede repetir una talla"
            )

        if variante.stock < 0:
            raise HTTPException(
                status_code=400,
                detail="El stock no puede ser negativo"
            )

        tallas_utilizadas.add(talla)

        variantes.append(
            {
                "size": talla,
                "stock": variante.stock
            }
        )

    return {
        "name": nombre,
        "description": solicitud.description,
        "category": categoria,
        "price": precio,
        "images": [
            str(imagen)
            for imagen in (solicitud.images or [])
        ],
        "variants": variantes
    }


def cargar_producto(db, producto_id: str):
    return db.scalar(
        select(ProductDB)
        .options(selectinload(ProductDB.variants))
        .where(ProductDB.id == producto_id)
        .execution_options(populate_existing=True)
    )


def buscar_pedido_activo(db, producto_id: str):
    """
    Comprueba si el producto aparece en algun pedido
    que todavia tiene un estado activo.
    """
    return db.scalar(
        select(OrderDB.id)
        .join(
            OrderItemDB,
            OrderItemDB.order_id == OrderDB.id
        )
        .where(
            OrderItemDB.product_id == producto_id,
            OrderDB.status.in_([
                "pending",
                "paid",
                "preparing",
                "shipped"
            ])
        )
        .limit(1)
    )


# ============================================================
# IMPLEMENTACION DE PRODUCTOS
# ============================================================

class ProductosApiImpl(BaseProductosApi):

    # GET /products
    async def get_products(
        self,
        category: str | None
    ) -> list[Product]:

        with SessionLocal() as db:
            consulta = (
                select(ProductDB)
                .options(selectinload(ProductDB.variants))
            )

            if category and category.strip():
                consulta = consulta.where(
                    ProductDB.category.ilike(
                        category.strip()
                    )
                )

            consulta = consulta.order_by(
                ProductDB.name,
                ProductDB.id
            )

            productos = db.scalars(consulta).all()

            return [
                convertir_producto(producto)
                for producto in productos
            ]

    # POST /products
    async def create_product(
        self,
        create_product_request: CreateProductRequest
    ) -> Product:

        datos = validar_producto(
            create_product_request
        )

        with SessionLocal() as db:
            producto = ProductDB(
                id=f"prod_{uuid4().hex}",
                name=datos["name"],
                description=datos["description"],
                category=datos["category"],
                price=datos["price"],
                images=datos["images"]
            )

            for variante in datos["variants"]:
                producto.variants.append(
                    ProductVariantDB(
                        size=variante["size"],
                        stock=variante["stock"]
                    )
                )

            db.add(producto)
            db.commit()

            producto = cargar_producto(
                db,
                producto.id
            )

            return convertir_producto(producto)

    # GET /products/{id}
    async def get_product_by_id(
        self,
        id: str
    ) -> Product:

        with SessionLocal() as db:
            producto = cargar_producto(db, id)

            if producto is None:
                raise HTTPException(
                    status_code=404,
                    detail="Producto no encontrado"
                )

            return convertir_producto(producto)

    # PUT /products/{id}
    async def update_product(
        self,
        id: str,
        create_product_request: CreateProductRequest
    ) -> Product:

        datos = validar_producto(
            create_product_request
        )

        with SessionLocal() as db:
            # Bloquear el producto para coordinar
            # modificaciones con compras simultaneas.
            producto = db.scalar(
                select(ProductDB)
                .where(ProductDB.id == id)
                .with_for_update()
            )

            if producto is None:
                raise HTTPException(
                    status_code=404,
                    detail="Producto no encontrado"
                )

            producto.name = datos["name"]
            producto.description = datos["description"]
            producto.category = datos["category"]
            producto.price = datos["price"]

            campos = create_product_request.model_fields_set

            if "images" in campos:
                producto.images = datos["images"]

            # Si no se envian variantes, conservamos el stock.
            if "variants" in campos:

                # Impedir cambios en el inventario mientras
                # existan pedidos activos de este producto.
                pedido_activo = buscar_pedido_activo(
                    db,
                    id
                )

                if pedido_activo is not None:
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            "No se puede modificar el inventario "
                            "de un producto con pedidos activos"
                        )
                    )

                # Recuperar las variantes existentes.
                variantes_actuales = list(producto.variants)

                # Eliminar primero las variantes antiguas.
                for variante in variantes_actuales:
                    db.delete(variante)

                # Ejecutar los DELETE antes de insertar
                # para evitar conflictos UNIQUE.
                db.flush()

                # Limpiar la coleccion en memoria.
                producto.variants = []

                # Insertar las nuevas variantes.
                for variante in datos["variants"]:
                    producto.variants.append(
                        ProductVariantDB(
                            size=variante["size"],
                            stock=variante["stock"]
                        )
                    )

            db.commit()

            producto = cargar_producto(db, id)

            return convertir_producto(producto)

    # DELETE /products/{id}
    async def delete_product(
        self,
        id: str
    ) -> None:

        with SessionLocal() as db:
            # Bloquear el producto antes de eliminarlo.
            producto = db.scalar(
                select(ProductDB)
                .where(ProductDB.id == id)
                .with_for_update()
            )

            if producto is None:
                raise HTTPException(
                    status_code=404,
                    detail="Producto no encontrado"
                )

            # No eliminar productos con pedidos activos.
            pedido_activo = buscar_pedido_activo(
                db,
                id
            )

            if pedido_activo is not None:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "No se puede eliminar un producto "
                        "con pedidos activos"
                    )
                )

            db.delete(producto)
            db.commit()

        return None
