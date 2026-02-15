from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import EightDigitId


# ── Request ─────────────────────────────────────────────────────────────────
class StudentCreate(BaseModel):
    id: EightDigitId
    class_id: EightDigitId
    full_name: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [{"id": 11112222, "class_id": 20000001, "full_name": "John Doe"}]
        }
    }


class StudentUpdate(BaseModel):
    full_name: str | None = None
    class_id: EightDigitId | None = None


# ── Response ────────────────────────────────────────────────────────────────
class StudentResponse(BaseModel):
    id: int
    class_id: int
    full_name: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
