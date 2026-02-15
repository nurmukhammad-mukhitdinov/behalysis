from datetime import datetime

from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class ClassRoom(Base):
    __tablename__ = "classrooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    school_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False
    )
    class_index: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    school: Mapped["School"] = relationship("School", back_populates="classrooms")  # noqa: F821
    students: Mapped[list["Student"]] = relationship(  # noqa: F821
        "Student", back_populates="classroom", cascade="all, delete-orphan"
    )
    lesson_reports: Mapped[list["LessonReport"]] = relationship(  # noqa: F821
        "LessonReport", back_populates="classroom", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ClassRoom id={self.id} class_index={self.class_index!r}>"
