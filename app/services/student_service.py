from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate


async def create_student(db: AsyncSession, data: StudentCreate) -> Student:
    existing = await db.get(Student, data.id)
    if existing:
        raise HTTPException(status_code=409, detail=f"Student {data.id} already exists")
    student = Student(id=data.id, class_id=data.class_id, full_name=data.full_name)
    db.add(student)
    await db.flush()
    await db.refresh(student)
    return student


async def get_students(db: AsyncSession, class_id: int | None = None) -> list[Student]:
    stmt = select(Student)
    if class_id is not None:
        stmt = stmt.where(Student.class_id == class_id)
    stmt = stmt.order_by(Student.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_student(db: AsyncSession, student_id: int) -> Student:
    student = await db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    return student


async def update_student(db: AsyncSession, student_id: int, data: StudentUpdate) -> Student:
    student = await get_student(db, student_id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(student, key, value)
    await db.flush()
    await db.refresh(student)
    return student


async def delete_student(db: AsyncSession, student_id: int) -> None:
    student = await get_student(db, student_id)
    await db.delete(student)
    await db.flush()


async def get_or_create_student(
    db: AsyncSession, student_id: int, class_id: int, full_name: str | None = None
) -> Student:
    """Get student or create a stub."""
    student = await db.get(Student, student_id)
    if not student:
        student = Student(id=student_id, class_id=class_id, full_name=full_name)
        db.add(student)
        await db.flush()
    return student
