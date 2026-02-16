import uuid
from datetime import datetime

from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class AttentionEntry(Base):
    __tablename__ = "attention_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    report_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("lesson_reports.id", ondelete="CASCADE"),
        nullable=False,
    )
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    attention: Mapped[int] = mapped_column(Integer, nullable=False)
    inattention: Mapped[int] = mapped_column(Integer, nullable=False)
    image_path: Mapped[str | None] = mapped_column(String(...), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    report: Mapped["LessonReport"] = relationship(  # noqa: F821
        "LessonReport", back_populates="attention_entries"
    )
    student: Mapped["Student"] = relationship(  # noqa: F821
        "Student", back_populates="attention_entries"
    )

    def __repr__(self) -> str:
        return f"<AttentionEntry id={self.id} student_id={self.student_id} attn={self.attention}>"
