from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.class_room import ClassRoom
from app.schemas.class_room import ClassRoomCreate, ClassRoomUpdate


async def create_class(db: AsyncSession, data: ClassRoomCreate) -> ClassRoom:
    existing = await db.get(ClassRoom, data.id)
    if existing:
        raise HTTPException(status_code=409, detail=f"ClassRoom {data.id} already exists")
    classroom = ClassRoom(id=data.id, school_id=data.school_id, class_index=data.class_index)
    db.add(classroom)
    await db.flush()
    await db.refresh(classroom)
    return classroom


async def get_classes(db: AsyncSession, school_id: int | None = None) -> list[ClassRoom]:
    stmt = select(ClassRoom)
    if school_id is not None:
        stmt = stmt.where(ClassRoom.school_id == school_id)
    stmt = stmt.order_by(ClassRoom.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_class(db: AsyncSession, class_id: int) -> ClassRoom:
    classroom = await db.get(ClassRoom, class_id)
    if not classroom:
        raise HTTPException(status_code=404, detail=f"ClassRoom {class_id} not found")
    return classroom


async def update_class(db: AsyncSession, class_id: int, data: ClassRoomUpdate) -> ClassRoom:
    classroom = await get_class(db, class_id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(classroom, key, value)
    await db.flush()
    await db.refresh(classroom)
    return classroom


async def delete_class(db: AsyncSession, class_id: int) -> None:
    classroom = await get_class(db, class_id)
    await db.delete(classroom)
    await db.flush()


async def get_or_create_class(
    db: AsyncSession, class_id: int, school_id: int, class_index: str
) -> ClassRoom:
    """Get classroom or create a stub."""
    classroom = await db.get(ClassRoom, class_id)
    if not classroom:
        classroom = ClassRoom(id=class_id, school_id=school_id, class_index=class_index)
        db.add(classroom)
        await db.flush()
    return classroom
