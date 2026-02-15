from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.school import School
from app.schemas.school import SchoolCreate, SchoolUpdate


async def create_school(db: AsyncSession, data: SchoolCreate) -> School:
    existing = await db.get(School, data.id)
    if existing:
        raise HTTPException(status_code=409, detail=f"School {data.id} already exists")
    school = School(id=data.id, name=data.name)
    db.add(school)
    await db.flush()
    await db.refresh(school)
    return school


async def get_schools(db: AsyncSession) -> list[School]:
    result = await db.execute(select(School).order_by(School.created_at.desc()))
    return list(result.scalars().all())


async def get_school(db: AsyncSession, school_id: int) -> School:
    school = await db.get(School, school_id)
    if not school:
        raise HTTPException(status_code=404, detail=f"School {school_id} not found")
    return school


async def update_school(db: AsyncSession, school_id: int, data: SchoolUpdate) -> School:
    school = await get_school(db, school_id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(school, key, value)
    await db.flush()
    await db.refresh(school)
    return school


async def delete_school(db: AsyncSession, school_id: int) -> None:
    school = await get_school(db, school_id)
    await db.delete(school)
    await db.flush()


async def get_or_create_school(db: AsyncSession, school_id: int) -> School:
    """Get school or create a stub if it doesn't exist (used by lesson report intake)."""
    school = await db.get(School, school_id)
    if not school:
        school = School(id=school_id)
        db.add(school)
        await db.flush()
    return school
