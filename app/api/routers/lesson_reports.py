import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.common import EightDigitId, MessageResponse, PaginatedResponse
from app.schemas.lesson_report import (
    LessonReportCreate,
    LessonReportUpdate,
    LessonReportResponse,
    LessonReportSummaryResponse,
    StudentEntryResponse,
    UnrecognizedEntryResponse,
)
from app.services import lesson_report_service
from app.core.config import settings

router = APIRouter(tags=["Lesson Reports"])


def _build_image_url(report_id: uuid.UUID, image_path: str | None) -> str | None:
    if not image_path:
        return None
    return f"/images/{report_id}/{image_path}"


def _report_to_response(report) -> LessonReportResponse:
    """Convert an ORM LessonReport (with entries loaded) into the response schema."""
    students = [
        StudentEntryResponse(
            id=e.id,
            student_id=e.student_id,
            attention=e.attention,
            inattention=e.inattention,
            image_url=_build_image_url(report.id, e.image_path),
            created_at=e.created_at,
        )
        for e in report.attention_entries
    ]
    unrecognized = [
        UnrecognizedEntryResponse(
            id=e.id,
            attention=e.attention,
            inattention=e.inattention,
            image_url=_build_image_url(report.id, e.image_path),
            created_at=e.created_at,
        )
        for e in report.unrecognized_entries
    ]
    return LessonReportResponse(
        id=report.id,
        school_id=report.school_id,
        class_id=report.class_id,
        class_index=report.class_index,
        lesson_date=report.lesson_date,
        lesson_time=report.lesson_time,
        students_count=report.students_count,
        avg_attention=report.avg_attention,
        avg_inattention=report.avg_inattention,
        created_at=report.created_at,
        students=students,
        unrecognized_students=unrecognized,
    )


# ── Lesson Reports CRUD ────────────────────────────────────────────────────
@router.post("/lesson-reports", response_model=LessonReportResponse, status_code=201)
async def create_lesson_report(
    data: LessonReportCreate, db: AsyncSession = Depends(get_db)
):
    report = await lesson_report_service.create_lesson_report(db, data)
    return _report_to_response(report)


@router.get("/lesson-reports", response_model=PaginatedResponse[LessonReportSummaryResponse])
async def list_lesson_reports(
    school_id: EightDigitId | None = Query(None),
    class_id: EightDigitId | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    reports, total = await lesson_report_service.get_lesson_reports(
        db,
        school_id=school_id,
        class_id=class_id,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
    return PaginatedResponse(
        items=[LessonReportSummaryResponse.model_validate(r) for r in reports],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/lesson-reports/{report_id}", response_model=LessonReportResponse)
async def get_lesson_report(report_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    report = await lesson_report_service.get_lesson_report(db, report_id)
    return _report_to_response(report)


@router.put("/lesson-reports/{report_id}", response_model=LessonReportResponse)
async def update_lesson_report(
    report_id: uuid.UUID,
    data: LessonReportUpdate,
    db: AsyncSession = Depends(get_db),
):
    report = await lesson_report_service.update_lesson_report(db, report_id, data)
    return _report_to_response(report)


@router.delete("/lesson-reports/{report_id}", response_model=MessageResponse)
async def delete_lesson_report(
    report_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    await lesson_report_service.delete_lesson_report(db, report_id)
    return MessageResponse(detail=f"LessonReport {report_id} deleted")


# ── Latest per class ────────────────────────────────────────────────────────
@router.get(
    "/classes/{class_id}/lesson-reports/latest",
    response_model=LessonReportResponse,
    tags=["Classes"],
)
async def get_latest_report_for_class(
    class_id: EightDigitId, db: AsyncSession = Depends(get_db)
):
    report = await lesson_report_service.get_latest_report_for_class(db, class_id)
    return _report_to_response(report)


# ── Image serving ──────────────────────────────────────────────────────────
@router.get("/images/{report_id}/{filename}", tags=["Images"])
async def get_image(report_id: uuid.UUID, filename: str):
    filepath = settings.IMAGES_DIR / str(report_id) / filename
    if not filepath.is_file():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(str(filepath))
