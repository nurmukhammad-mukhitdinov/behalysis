from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import EightDigitId


# ── Request ─────────────────────────────────────────────────────────────────
class SchoolCreate(BaseModel):
    id: EightDigitId
    name: str | None = None

    model_config = {"json_schema_extra": {"examples": [{"id": 10000001, "name": "School #1"}]}}


class SchoolUpdate(BaseModel):
    name: str | None = None


# ── Response ────────────────────────────────────────────────────────────────
class SchoolResponse(BaseModel):
    id: int
    name: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
