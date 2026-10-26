
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)


class Base(DeclarativeBase):
    pass


# Tabla de artistas
class ArtistDB(Base):
    __tablename__ = "artists"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    genre: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    biography: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    songs: Mapped[list["SongDB"]] = relationship(
        back_populates="artist",
        cascade="all, delete-orphan"
    )


# Tabla de canciones
class SongDB(Base):
    __tablename__ = "songs"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    artist_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("artists.id"),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    spotify_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    spotify_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    preview_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    artist: Mapped["ArtistDB"] = relationship(
        back_populates="songs"
    )
