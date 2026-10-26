
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    String
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column
)


class Base(DeclarativeBase):
    pass


class UserDB(Base):

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="client",
        nullable=False
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
