import shutil
import uuid
from datetime import date

from fastapi import HTTPException
from sqlalchemy import select, func, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.lesson_report import LessonReport
from app.models.attention_entry import AttentionEntry
from app.models.unrecognized_entry import UnrecognizedEntry
from app.schemas.lesson_report import LessonReportCreate, LessonReportUpdate
from app.services.school_service import get_or_create_school
from app.services.class_service import get_or_create_class
from app.services.student_service import get_or_create_student
from app.utils.images import save_image, get_report_image_dir
from app.core.config import settings
from app.core.logging import logger


async def create_lesson_report(
    db: AsyncSession, data: LessonReportCreate
) -> LessonReport:
    """Process a full lesson report from CV, save images, compute metrics."""
    # Use server date if not provided
    report_date = data.lesson_date or date.today()

    # Auto-create school / classroom if they don't exist
    await get_or_create_school(db, data.school_id)
    await get_or_create_class(db, data.class_id, data.school_id, data.class_index)

    # Create report
    report_id = uuid.uuid4()
    report = LessonReport(
        id=report_id,
        school_id=data.school_id,
        class_id=data.class_id,
        class_index=data.class_index,
        lesson_date=report_date,
        lesson_time=data.lesson_time,
        students_count=data.students_count,
        avg_attention=0.0,
        avg_inattention=0.0,
    )
    db.add(report)
    await db.flush()

    report_dir = get_report_image_dir(report_id)
    all_attentions: list[int] = []

    # Process recognized students
    for entry in data.students:
        await get_or_create_student(db, entry.student_id, data.class_id, entry.name)
        filename = save_image(entry.image, report_dir) if entry.image else None
        inattention = 100 - entry.attention
        ae = AttentionEntry(
            report_id=report_id,
            student_id=entry.student_id,
            attention=entry.attention,
            inattention=inattention,
            image_path=filename,
        )
        db.add(ae)
        all_attentions.append(entry.attention)

    # Process unrecognized students
    for entry in data.unrecognized_students:
        filename = save_image(entry.image, report_dir) if entry.image else None
        inattention = 100 - entry.attention
        ue = UnrecognizedEntry(
            report_id=report_id,
            attention=entry.attention,
            inattention=inattention,
            image_path=filename,
        )
        db.add(ue)
        all_attentions.append(entry.attention)

    # Compute averages
    if all_attentions:
        avg_attn = sum(all_attentions) / len(all_attentions)
        report.avg_attention = round(avg_attn, 2)
        report.avg_inattention = round(100 - avg_attn, 2)

    await db.flush()
    logger.info("Created lesson report %s for class %s", report_id, data.class_index)

    return await _load_full_report(db, report_id)


async def get_lesson_reports(
    db: AsyncSession,
    school_id: int | None = None,
    class_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[LessonReport], int]:
    """Return filtered list of reports with total count."""
    stmt = select(LessonReport)
    count_stmt = select(func.count(LessonReport.id))

    conditions = []
    if school_id is not None:
        conditions.append(LessonReport.school_id == school_id)
    if class_id is not None:
        conditions.append(LessonReport.class_id == class_id)
    if date_from is not None:
        conditions.append(LessonReport.lesson_date >= date_from)
    if date_to is not None:
        conditions.append(LessonReport.lesson_date <= date_to)

    for cond in conditions:
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)

    total = (await db.execute(count_stmt)).scalar() or 0
    stmt = stmt.order_by(LessonReport.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def get_lesson_report(db: AsyncSession, report_id: uuid.UUID) -> LessonReport:
    report = await _load_full_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"LessonReport {report_id} not found")
    return report


async def update_lesson_report(
    db: AsyncSession, report_id: uuid.UUID, data: LessonReportUpdate
) -> LessonReport:
    """Replace entries and recompute metrics if students are provided."""
    report = await _load_full_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"LessonReport {report_id} not found")

    # Update scalar fields
    for field in ("class_id", "school_id", "class_index", "lesson_time", "lesson_date", "students_count"):
        val = getattr(data, field, None)
        if val is not None:
            setattr(report, field, val)

    # If students list is provided, replace entries
    if data.students is not None:
        # Delete old entries + images
        await db.execute(
            sa_delete(AttentionEntry).where(AttentionEntry.report_id == report_id)
        )
        await db.execute(
            sa_delete(UnrecognizedEntry).where(UnrecognizedEntry.report_id == report_id)
        )

        # Remove old images folder and recreate
        report_dir = get_report_image_dir(report_id)
        shutil.rmtree(report_dir, ignore_errors=True)
        report_dir.mkdir(parents=True, exist_ok=True)

        all_attentions: list[int] = []

        for entry in data.students:
            await get_or_create_student(db, entry.student_id, report.class_id, entry.name)
            filename = save_image(entry.image, report_dir) if entry.image else None
            inattention = 100 - entry.attention
            ae = AttentionEntry(
                report_id=report_id,
                student_id=entry.student_id,
                attention=entry.attention,
                inattention=inattention,
                image_path=filename,
            )
            db.add(ae)
            all_attentions.append(entry.attention)

        unrec = data.unrecognized_students or []
        for entry in unrec:
            filename = save_image(entry.image, report_dir) if entry.image else None
            inattention = 100 - entry.attention
            ue = UnrecognizedEntry(
                report_id=report_id,
                attention=entry.attention,
                inattention=inattention,
                image_path=filename,
            )
            db.add(ue)
            all_attentions.append(entry.attention)

        if all_attentions:
            avg_attn = sum(all_attentions) / len(all_attentions)
            report.avg_attention = round(avg_attn, 2)
            report.avg_inattention = round(100 - avg_attn, 2)

    await db.flush()
    return await _load_full_report(db, report_id)


async def delete_lesson_report(db: AsyncSession, report_id: uuid.UUID) -> None:
    report = await _load_full_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"LessonReport {report_id} not found")

    # Remove images from disk
    report_dir = settings.IMAGES_DIR / str(report_id)
    shutil.rmtree(report_dir, ignore_errors=True)

    await db.delete(report)
    await db.flush()


async def get_latest_report_for_class(
    db: AsyncSession, class_id: int
) -> LessonReport | None:
    """Return the most recent report for a given class, with entries loaded."""
    stmt = (
        select(LessonReport)
        .where(LessonReport.class_id == class_id)
        .order_by(LessonReport.created_at.desc())
        .limit(1)
        .options(
            selectinload(LessonReport.attention_entries),
            selectinload(LessonReport.unrecognized_entries),
        )
    )
    result = await db.execute(stmt)
    report = result.scalars().first()
    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"No lesson reports found for class {class_id}",
        )
    return report


async def _load_full_report(
    db: AsyncSession, report_id: uuid.UUID
) -> LessonReport | None:
    """Load a report with its entries eagerly."""
    stmt = (
        select(LessonReport)
        .where(LessonReport.id == report_id)
        .options(
            selectinload(LessonReport.attention_entries),
            selectinload(LessonReport.unrecognized_entries),
        )
    )
    result = await db.execute(stmt)
    return result.scalars().first()
