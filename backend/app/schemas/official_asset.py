import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SocialPlatform(str, Enum):
    X = "x"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"


class AppStore(str, Enum):
    GOOGLE_PLAY = "google_play"
    APP_STORE = "app_store"


class OfficialSocialAccountCreate(BaseModel):
    platform: SocialPlatform = Field(..., description="Social media platform")
    raw_handle: str = Field(..., min_length=1, max_length=255, description="Account handle as displayed (e.g. @Nike)")
    url: str | None = Field(default=None, description="Direct URL to official account profile")
    is_verified: bool = Field(default=False, description="Whether the account has verified badge status on platform")

    @field_validator("raw_handle")
    @classmethod
    def validate_raw_handle(cls, v: str) -> str:
        trimmed = v.strip()
        cleaned = trimmed.lstrip("@").strip()
        if not cleaned:
            raise ValueError("Handle must contain at least one non-whitespace character other than '@'")
        return trimmed


class OfficialSocialAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    brand_id: uuid.UUID
    platform: str
    handle: str
    raw_handle: str
    url: str | None = None
    is_verified: bool = False
    created_at: datetime


class OfficialAppCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Official app name")
    package_id: str | None = Field(default=None, max_length=255, description="Package / Bundle ID (e.g. com.nike.omega)")
    developer_name: str = Field(..., min_length=1, max_length=255, description="Official developer or publisher name")
    store: AppStore = Field(..., description="App store platform (google_play or app_store)")
    store_url: str | None = Field(default=None, description="App store listing URL")
    logo_url: str | None = Field(default=None, description="App icon image URL")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("App name must not be blank")
        return trimmed

    @field_validator("developer_name")
    @classmethod
    def validate_developer_name(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Developer name must not be blank")
        return trimmed


class OfficialAppResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    brand_id: uuid.UUID
    name: str
    package_id: str | None = None
    developer_name: str
    store: str
    store_url: str | None = None
    logo_url: str | None = None
    created_at: datetime
