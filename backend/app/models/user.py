import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import String, DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.brand import Brand


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships with selectin loading for async safety
    brands: Mapped[List["Brand"]] = relationship(
        "Brand",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
