import uuid
from datetime import date, time, datetime
from typing import Self

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import EightDigitId


# ── Nested entry schemas ────────────────────────────────────────────────────
class StudentEntryCreate(BaseModel):
    student_id: EightDigitId
    name: str | None = None
    image: str = Field(..., description="Base64-encoded image")
    attention: int = Field(..., ge=1, le=100)


class UnrecognizedEntryCreate(BaseModel):
    image: str = Field(..., description="Base64-encoded image")
    attention: int = Field(..., ge=1, le=100)


class StudentEntryResponse(BaseModel):
    id: uuid.UUID
    student_id: int
    attention: int
    inattention: int
    image_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UnrecognizedEntryResponse(BaseModel):
    id: uuid.UUID
    attention: int
    inattention: int
    image_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Lesson Report ───────────────────────────────────────────────────────────
class LessonReportCreate(BaseModel):
    class_id: EightDigitId
    school_id: EightDigitId
    class_index: str
    lesson_time: time
    lesson_date: date | None = None
    students_count: int = Field(..., ge=0)
    students: list[StudentEntryCreate]
    unrecognized_students: list[UnrecognizedEntryCreate] = []

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "class_id": 12345678,
                    "school_id": 87654321,
                    "class_index": "8-E",
                    "lesson_time": "09:30:00",
                    "lesson_date": "2026-02-15",
                    "students_count": 2,
                    "students": [
                        {
                            "student_id": 11112222,
                            "name": "Alice",
                            "image": "<base64>",
                            "attention": 85,
                        }
                    ],
                    "unrecognized_students": [
                        {"image": "<base64>", "attention": 60}
                    ],
                }
            ]
        }
    }

    @model_validator(mode="after")
    def check_students_count(self) -> Self:
        actual = len(self.students) + len(self.unrecognized_students)
        if self.students_count != actual:
            raise ValueError(
                f"students_count ({self.students_count}) must equal "
                f"len(students) + len(unrecognized_students) ({actual})"
            )
        return self


class LessonReportUpdate(BaseModel):
    class_id: EightDigitId | None = None
    school_id: EightDigitId | None = None
    class_index: str | None = None
    lesson_time: time | None = None
    lesson_date: date | None = None
    students_count: int | None = Field(None, ge=0)
    students: list[StudentEntryCreate] | None = None
    unrecognized_students: list[UnrecognizedEntryCreate] | None = None

    @model_validator(mode="after")
    def check_students_count(self) -> Self:
        if self.students is not None and self.students_count is not None:
            unrec = self.unrecognized_students or []
            actual = len(self.students) + len(unrec)
            if self.students_count != actual:
                raise ValueError(
                    f"students_count ({self.students_count}) must equal "
                    f"len(students) + len(unrecognized_students) ({actual})"
                )
        return self


class LessonReportResponse(BaseModel):
    id: uuid.UUID
    school_id: int
    class_id: int
    class_index: str
    lesson_date: date
    lesson_time: time
    students_count: int
    avg_attention: float
    avg_inattention: float
    created_at: datetime
    students: list[StudentEntryResponse] = []
    unrecognized_students: list[UnrecognizedEntryResponse] = []

    model_config = {"from_attributes": True}


class LessonReportSummaryResponse(BaseModel):
    """Lightweight response without nested entries (for list views)."""
    id: uuid.UUID
    school_id: int
    class_id: int
    class_index: str
    lesson_date: date
    lesson_time: time
    students_count: int
    avg_attention: float
    avg_inattention: float
    created_at: datetime

    model_config = {"from_attributes": True}
