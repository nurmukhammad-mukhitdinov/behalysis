from app.db.base_class import Base  # noqa: F401

# Import all models so Alembic and Base.metadata can discover them.
from app.models.school import School  # noqa: F401
from app.models.class_room import ClassRoom  # noqa: F401
from app.models.student import Student  # noqa: F401
from app.models.lesson_report import LessonReport  # noqa: F401
from app.models.attention_entry import AttentionEntry  # noqa: F401
from app.models.unrecognized_entry import UnrecognizedEntry  # noqa: F401
