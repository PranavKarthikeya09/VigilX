"""initial schema for vigilX

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-12 15:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    # 1. Users Table
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 2. Brands Table
    op.create_table(
        "brands",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("normalized_name", sa.String(length=255), nullable=False),
        sa.Column("logo_url", sa.Text(), nullable=True),
        sa.Column("logo_phash", sa.String(length=64), nullable=True),
        sa.Column("website", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_brands_owner_id", "brands", ["owner_id"], unique=False)
    op.create_index("ix_brands_normalized_name", "brands", ["normalized_name"], unique=False)

    # 3. Official Social Accounts Table
    op.create_table(
        "official_social_accounts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("brand_id", sa.UUID(), nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=False),
        sa.Column("handle", sa.String(length=255), nullable=False),
        sa.Column("raw_handle", sa.String(length=255), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["brand_id"], ["brands.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("brand_id", "platform", "handle", name="uq_official_social_brand_platform_handle"),
    )
    op.create_index("ix_official_social_accounts_brand_id", "official_social_accounts", ["brand_id"], unique=False)

    # 4. Official Apps Table
    op.create_table(
        "official_apps",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("brand_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("package_id", sa.String(length=255), nullable=True),
        sa.Column("developer_name", sa.String(length=255), nullable=False),
        sa.Column("store", sa.String(length=50), nullable=False),
        sa.Column("store_url", sa.Text(), nullable=True),
        sa.Column("logo_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["brand_id"], ["brands.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_official_apps_brand_id", "official_apps", ["brand_id"], unique=False)
    op.create_index("ix_official_apps_package_id", "official_apps", ["package_id"], unique=False)

    # 5. Detections Table
    op.create_table(
        "detections",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("brand_id", sa.UUID(), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("handle_or_package", sa.String(length=255), nullable=True),
        sa.Column("developer_or_owner", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("logo_url", sa.Text(), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="needs_review"),
        sa.Column("is_official_excluded", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("raw_signals", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["brand_id"], ["brands.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_detections_brand_id", "detections", ["brand_id"], unique=False)
    op.create_index("ix_detections_risk_score", "detections", ["risk_score"], unique=False)
    op.create_index("ix_detections_risk_level", "detections", ["risk_level"], unique=False)
    op.create_index("ix_detections_status", "detections", ["status"], unique=False)
    op.create_index("ix_detections_source_type", "detections", ["source_type"], unique=False)
    op.create_index("ix_detections_platform", "detections", ["platform"], unique=False)

    # 6. Detection Evidence Table
    op.create_table(
        "detection_evidence",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("detection_id", sa.UUID(), nullable=False),
        sa.Column("signal_type", sa.String(length=50), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["detection_id"], ["detections.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_detection_evidence_detection_id", "detection_evidence", ["detection_id"], unique=False)


def downgrade() -> None:
    op.drop_table("detection_evidence")
    op.drop_table("detections")
    op.drop_table("official_apps")
    op.drop_table("official_social_accounts")
    op.drop_table("brands")
    op.drop_table("users")
