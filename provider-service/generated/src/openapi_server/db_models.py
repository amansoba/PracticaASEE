
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)


# ============================================================
# CLASE BASE
# ============================================================

class Base(DeclarativeBase):
    pass


# ============================================================
# PROVEEDORES
# ============================================================

class ProviderDB(Base):
    __tablename__ = "providers"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    # Referencia a auth-service
    user_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    company_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    cif_nif: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
    )

    service_category: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    contact_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    proposals: Mapped[list["SpaceProposalDB"]] = relationship(
        back_populates="provider"
    )


# ============================================================
# SERVICIOS EXTERNOS
# ============================================================

class ExternalServiceDB(Base):
    __tablename__ = "external_services"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )


# ============================================================
# ESPACIOS ALQUILABLES
# ============================================================

class SpaceDB(Base):
    __tablename__ = "spaces"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    # Referencia a event-service.
    # No es FK local porque pertenece a otro microservicio.
    event_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    dimensions: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    base_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    is_available: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    proposals: Mapped[list["SpaceProposalDB"]] = relationship(
        back_populates="space"
    )

    __table_args__ = (
        CheckConstraint(
            "base_price >= 0",
            name="ck_spaces_base_price_nonnegative"
        ),
        UniqueConstraint(
            "event_id",
            "name",
            name="uq_space_event_name"
        ),
    )


# ============================================================
# PROPUESTAS Y PRESUPUESTOS
# ============================================================

class SpaceProposalDB(Base):
    __tablename__ = "space_proposals"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    space_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("spaces.id"),
        nullable=False,
        index=True
    )

    provider_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("providers.id"),
        nullable=False,
        index=True
    )

    # Referencia al evento externo
    event_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    budget_proposal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    setup_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending"
    )

    provider: Mapped["ProviderDB"] = relationship(
        back_populates="proposals"
    )

    space: Mapped["SpaceDB"] = relationship(
        back_populates="proposals"
    )

    __table_args__ = (
        CheckConstraint(
            "budget_proposal >= 0",
            name="ck_proposal_budget_nonnegative"
        ),
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="ck_proposal_status_valid"
        ),
    )
