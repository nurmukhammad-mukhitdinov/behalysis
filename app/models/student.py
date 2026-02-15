from datetime import datetime

from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    class_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False
    )
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    classroom: Mapped["ClassRoom"] = relationship("ClassRoom", back_populates="students")  # noqa: F821
    attention_entries: Mapped[list["AttentionEntry"]] = relationship(  # noqa: F821
        "AttentionEntry", back_populates="student", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Student id={self.id} full_name={self.full_name!r}>"
