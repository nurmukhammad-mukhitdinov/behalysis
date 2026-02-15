"""Initial schema: all tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-02-15
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Schools ──────────────────────────────────────────────────────────
    op.create_table(
        "schools",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── ClassRooms ───────────────────────────────────────────────────────
    op.create_table(
        "classrooms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("school_id", sa.Integer(), nullable=False),
        sa.Column("class_index", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"], ondelete="CASCADE"),
    )

    # ── Students ─────────────────────────────────────────────────────────
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["class_id"], ["classrooms.id"], ondelete="CASCADE"),
    )

    # ── Lesson Reports ───────────────────────────────────────────────────
    op.create_table(
        "lesson_reports",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("school_id", sa.Integer(), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("class_index", sa.String(50), nullable=False),
        sa.Column("lesson_date", sa.Date(), nullable=False),
        sa.Column("lesson_time", sa.Time(), nullable=False),
        sa.Column("students_count", sa.Integer(), nullable=False),
        sa.Column("avg_attention", sa.Float(), nullable=False, server_default="0"),
        sa.Column("avg_inattention", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["class_id"], ["classrooms.id"], ondelete="CASCADE"),
    )

    # ── Attention Entries (recognized) ───────────────────────────────────
    op.create_table(
        "attention_entries",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("report_id", UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("attention", sa.Integer(), nullable=False),
        sa.Column("inattention", sa.Integer(), nullable=False),
        sa.Column("image_path", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["report_id"], ["lesson_reports.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
    )

    # ── Unrecognized Entries ─────────────────────────────────────────────
    op.create_table(
        "unrecognized_entries",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("report_id", UUID(as_uuid=True), nullable=False),
        sa.Column("attention", sa.Integer(), nullable=False),
        sa.Column("inattention", sa.Integer(), nullable=False),
        sa.Column("image_path", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["report_id"], ["lesson_reports.id"], ondelete="CASCADE"),
    )

    # ── Indexes ──────────────────────────────────────────────────────────
    op.create_index("ix_classrooms_school_id", "classrooms", ["school_id"])
    op.create_index("ix_students_class_id", "students", ["class_id"])
    op.create_index("ix_lesson_reports_school_id", "lesson_reports", ["school_id"])
    op.create_index("ix_lesson_reports_class_id", "lesson_reports", ["class_id"])
    op.create_index("ix_lesson_reports_lesson_date", "lesson_reports", ["lesson_date"])
    op.create_index("ix_attention_entries_report_id", "attention_entries", ["report_id"])
    op.create_index("ix_unrecognized_entries_report_id", "unrecognized_entries", ["report_id"])


def downgrade() -> None:
    op.drop_table("unrecognized_entries")
    op.drop_table("attention_entries")
    op.drop_table("lesson_reports")
    op.drop_table("students")
    op.drop_table("classrooms")
    op.drop_table("schools")
