
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    JSON
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)


class Base(DeclarativeBase):
    pass


# ============================================================
# PRODUCTOS
# ============================================================

class ProductDB(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    images: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False
    )

    variants: Mapped[list["ProductVariantDB"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "price >= 0",
            name="ck_products_price_nonnegative"
        ),
    )


# ============================================================
# INVENTARIO POR TALLA
# ============================================================

class ProductVariantDB(Base):
    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    product_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    size: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    product: Mapped["ProductDB"] = relationship(
        back_populates="variants"
    )

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "size",
            name="uq_product_variant_size"
        ),
        CheckConstraint(
            "stock >= 0",
            name="ck_product_variants_stock_nonnegative"
        ),
    )


# ============================================================
# PEDIDOS
# ============================================================

class OrderDB(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    # Referencia al usuario propietario en auth-service
    user_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    shipping_address: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    payment_method_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    total_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    items: Mapped[list["OrderItemDB"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "total_price >= 0",
            name="ck_orders_total_nonnegative"
        ),
        CheckConstraint(
            "status IN ('pending', 'paid', 'preparing', "
            "'shipped', 'delivered', 'cancelled')",
            name="ck_orders_status_valid"
        ),
    )


# ============================================================
# ARTICULOS DE CADA PEDIDO
# ============================================================

class OrderItemDB(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    order_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("orders.id"),
        nullable=False,
        index=True
    )

    # Guardamos el ID sin clave foranea hacia products:
    # los pedidos deben conservar su historial aunque
    # se retire un producto del catalogo.
    product_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    size: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    # Precio historico, no el precio actual del producto
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    order: Mapped["OrderDB"] = relationship(
        back_populates="items"
    )

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_order_items_quantity_positive"
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_order_items_unit_price_nonnegative"
        ),
    )
