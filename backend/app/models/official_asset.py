import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.brand import Brand


class OfficialSocialAccount(Base):
    __tablename__ = "official_social_accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("brands.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    handle: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    raw_handle: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    brand: Mapped["Brand"] = relationship(
        "Brand",
        back_populates="social_accounts",
    )

    __table_args__ = (
        UniqueConstraint("brand_id", "platform", "handle", name="uq_official_social_brand_platform_handle"),
    )


class OfficialApp(Base):
    __tablename__ = "official_apps"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("brands.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    package_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    developer_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,  # Enforced required developer name per architecture decision
    )
    store: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # 'google_play', 'app_store'
    )
    store_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    logo_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    brand: Mapped["Brand"] = relationship(
        "Brand",
        back_populates="official_apps",
    )
