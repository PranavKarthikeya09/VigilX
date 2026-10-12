from datetime import datetime, timezone
from typing import Any, Generic, List, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    field: str
    issue: str


class StandardErrorResponse(BaseModel):
    status: int
    error_code: str
    message: str
    details: List[ErrorDetail] = Field(default_factory=list)
    request_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    app_name: str = "vigilX"


class ReadyResponse(BaseModel):
    status: str = "ready"
    database: str
    app_name: str = "vigilX"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    pagination: PaginationMeta
