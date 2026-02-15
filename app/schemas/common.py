from typing import Annotated, Any, Generic, TypeVar

from pydantic import BaseModel, Field

# ── 8-digit ID type ──────────────────────────────────────────────────────────
EightDigitId = Annotated[int, Field(ge=10_000_000, le=99_999_999, description="8-digit integer ID")]


# ── Error response ──────────────────────────────────────────────────────────
class ErrorResponse(BaseModel):
    detail: str


class ValidationErrorDetail(BaseModel):
    loc: list[str | int] = []
    msg: str
    type: str = "value_error"


class ValidationErrorResponse(BaseModel):
    detail: list[ValidationErrorDetail]


# ── Pagination ──────────────────────────────────────────────────────────────
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int


# ── Message response ────────────────────────────────────────────────────────
class MessageResponse(BaseModel):
    detail: str
