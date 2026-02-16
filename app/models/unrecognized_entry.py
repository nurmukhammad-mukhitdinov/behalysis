import uuid
from datetime import datetime

from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class UnrecognizedEntry(Base):
    __tablename__ = "unrecognized_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    report_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("lesson_reports.id", ondelete="CASCADE"),
        nullable=False,
    )
    attention: Mapped[int] = mapped_column(Integer, nullable=False)
    inattention: Mapped[int] = mapped_column(Integer, nullable=False)
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    report: Mapped["LessonReport"] = relationship(  # noqa: F821
        "LessonReport", back_populates="unrecognized_entries"
    )

    def __repr__(self) -> str:
        return f"<UnrecognizedEntry id={self.id} attn={self.attention}>"
