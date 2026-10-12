import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.official_asset import OfficialSocialAccount, OfficialApp
    from app.models.detection import Detection


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    normalized_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    logo_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    logo_phash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    website: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships with selectin loading for async safety
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="brands",
    )
    social_accounts: Mapped[List["OfficialSocialAccount"]] = relationship(
        "OfficialSocialAccount",
        back_populates="brand",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    official_apps: Mapped[List["OfficialApp"]] = relationship(
        "OfficialApp",
        back_populates="brand",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    detections: Mapped[List["Detection"]] = relationship(
        "Detection",
        back_populates="brand",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
