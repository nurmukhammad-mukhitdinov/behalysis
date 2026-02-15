from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from app.schemas.common import EightDigitId, MessageResponse
from app.services import student_service

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("", response_model=StudentResponse, status_code=201)
async def create_student(data: StudentCreate, db: AsyncSession = Depends(get_db)):
    return await student_service.create_student(db, data)


@router.get("", response_model=list[StudentResponse])
async def list_students(
    class_id: EightDigitId | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await student_service.get_students(db, class_id=class_id)


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: EightDigitId, db: AsyncSession = Depends(get_db)):
    return await student_service.get_student(db, student_id)


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: EightDigitId,
    data: StudentUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await student_service.update_student(db, student_id, data)


@router.delete("/{student_id}", response_model=MessageResponse)
async def delete_student(student_id: EightDigitId, db: AsyncSession = Depends(get_db)):
    await student_service.delete_student(db, student_id)
    return MessageResponse(detail=f"Student {student_id} deleted")
