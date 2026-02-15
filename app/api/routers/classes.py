from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.class_room import ClassRoomCreate, ClassRoomUpdate, ClassRoomResponse
from app.schemas.common import EightDigitId, MessageResponse
from app.services import class_service

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.post("", response_model=ClassRoomResponse, status_code=201)
async def create_class(data: ClassRoomCreate, db: AsyncSession = Depends(get_db)):
    return await class_service.create_class(db, data)


@router.get("", response_model=list[ClassRoomResponse])
async def list_classes(
    school_id: EightDigitId | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await class_service.get_classes(db, school_id=school_id)


@router.get("/{class_id}", response_model=ClassRoomResponse)
async def get_class(class_id: EightDigitId, db: AsyncSession = Depends(get_db)):
    return await class_service.get_class(db, class_id)


@router.put("/{class_id}", response_model=ClassRoomResponse)
async def update_class(
    class_id: EightDigitId, data: ClassRoomUpdate, db: AsyncSession = Depends(get_db)
):
    return await class_service.update_class(db, class_id, data)


@router.delete("/{class_id}", response_model=MessageResponse)
async def delete_class(class_id: EightDigitId, db: AsyncSession = Depends(get_db)):
    await class_service.delete_class(db, class_id)
    return MessageResponse(detail=f"ClassRoom {class_id} deleted")
