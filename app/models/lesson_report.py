import uuid
from datetime import date, time, datetime

from sqlalchemy import (
    Integer,
    String,
    Float,
    Date,
    Time,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class LessonReport(Base):
    __tablename__ = "lesson_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    school_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False
    )
    class_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False
    )
    class_index: Mapped[str] = mapped_column(String(50), nullable=False)
    lesson_date: Mapped[date] = mapped_column(Date, nullable=False)
    lesson_time: Mapped[time] = mapped_column(Time, nullable=False)
    students_count: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_attention: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_inattention: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="lesson_reports")  # noqa: F821
    classroom: Mapped["ClassRoom"] = relationship("ClassRoom", back_populates="lesson_reports")  # noqa: F821
    attention_entries: Mapped[list["AttentionEntry"]] = relationship(  # noqa: F821
        "AttentionEntry", back_populates="report", cascade="all, delete-orphan"
    )
    unrecognized_entries: Mapped[list["UnrecognizedEntry"]] = relationship(  # noqa: F821
        "UnrecognizedEntry", back_populates="report", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<LessonReport id={self.id} class_index={self.class_index!r} date={self.lesson_date}>"
