from datetime import datetime

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class School(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    classrooms: Mapped[list["ClassRoom"]] = relationship(  # noqa: F821
        "ClassRoom", back_populates="school", cascade="all, delete-orphan"
    )
    lesson_reports: Mapped[list["LessonReport"]] = relationship(  # noqa: F821
        "LessonReport", back_populates="school", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<School id={self.id} name={self.name!r}>"
