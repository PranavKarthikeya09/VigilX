import uuid
from datetime import datetime
from typing import Any, Dict, List, TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, Float, DateTime, ForeignKey, JSON, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.brand import Brand


class Detection(Base):
    __tablename__ = "detections"

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
    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # 'social' or 'app_store'
        index=True,
    )
    platform: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # 'x', 'instagram', 'google_play', 'app_store'
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )
    url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    handle_or_package: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    developer_or_owner: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    logo_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        index=True,
    )
    risk_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,  # 'high', 'medium', 'low'
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="needs_review",
        nullable=False,
        index=True,  # 'needs_review', 'reviewed', 'false_positive', 'escalated'
    )
    is_official_excluded: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    raw_signals: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
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

    # Relationships with selectin loading
    brand: Mapped["Brand"] = relationship(
        "Brand",
        back_populates="detections",
    )
    evidence_items: Mapped[List["DetectionEvidence"]] = relationship(
        "DetectionEvidence",
        back_populates="detection",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class DetectionEvidence(Base):
    __tablename__ = "detection_evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    detection_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("detections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    signal_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    metadata_json: Mapped[Dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    detection: Mapped["Detection"] = relationship(
        "Detection",
        back_populates="evidence_items",
    )
