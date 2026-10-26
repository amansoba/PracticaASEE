
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    JSON,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# Tabla de festivales
class EventDB(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    venue: Mapped[str] = mapped_column(String(200), nullable=False)
    location_city: Mapped[str] = mapped_column(String(100), nullable=False)


# Tabla de actuaciones del Line-up
class ScheduleEntryDB(Base):
    __tablename__ = "schedule_entries"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    event_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("events.id"),
        nullable=False
    )
    artist_id: Mapped[str] = mapped_column(String(50), nullable=False)
    artist_name: Mapped[str | None] = mapped_column(String(200))
    stage: Mapped[str] = mapped_column(String(100), nullable=False)
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )


# Tabla de tipos de pases
class PassConfigDB(Base):
    __tablename__ = "pass_configs"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    event_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("events.id"),
        nullable=False
    )
    type_name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    available_tickets: Mapped[int] = mapped_column(Integer, nullable=False)
    benefits: Mapped[list] = mapped_column(JSON, default=list)


# Tabla de entradas emitidas
class TicketDB(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    event_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("events.id"),
        nullable=False
    )
    pass_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("pass_configs.id"),
        nullable=False
    )
    user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    qr_code: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    purchased_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
