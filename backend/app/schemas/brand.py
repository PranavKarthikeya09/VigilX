import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


class BrandBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Brand name")
    website: str | None = Field(default=None, max_length=512, description="Official website URL")
    logo_url: str | None = Field(default=None, description="Official logo image URL")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        trimmed = v.strip()
        if len(trimmed) < 2:
            raise ValueError("Brand name must contain at least 2 non-whitespace characters")
        return trimmed


class BrandCreate(BrandBase):
    pass


class BrandResponse(BrandBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    normalized_name: str
    logo_phash: str | None = None
    created_at: datetime
    updated_at: datetime


class BrandDetailResponse(BrandResponse):
    official_social_count: int = 0
    official_app_count: int = 0
