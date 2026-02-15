from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import EightDigitId


# ── Request ─────────────────────────────────────────────────────────────────
class ClassRoomCreate(BaseModel):
    id: EightDigitId
    school_id: EightDigitId
    class_index: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"id": 20000001, "school_id": 10000001, "class_index": "8-E"}]
        }
    }


class ClassRoomUpdate(BaseModel):
    class_index: str | None = None
    school_id: EightDigitId | None = None


# ── Response ────────────────────────────────────────────────────────────────
class ClassRoomResponse(BaseModel):
    id: int
    school_id: int
    class_index: str
    created_at: datetime

    model_config = {"from_attributes": True}
