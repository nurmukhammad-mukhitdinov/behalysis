from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.school import SchoolCreate, SchoolUpdate, SchoolResponse
from app.schemas.common import EightDigitId, MessageResponse
from app.services import school_service

router = APIRouter(prefix="/schools", tags=["Schools"])


@router.post("", response_model=SchoolResponse, status_code=201)
async def create_school(data: SchoolCreate, db: AsyncSession = Depends(get_db)):
    return await school_service.create_school(db, data)


@router.get("", response_model=list[SchoolResponse])
async def list_schools(db: AsyncSession = Depends(get_db)):
    return await school_service.get_schools(db)


@router.get("/{school_id}", response_model=SchoolResponse)
async def get_school(school_id: EightDigitId, db: AsyncSession = Depends(get_db)):
    return await school_service.get_school(db, school_id)


@router.put("/{school_id}", response_model=SchoolResponse)
async def update_school(
    school_id: EightDigitId, data: SchoolUpdate, db: AsyncSession = Depends(get_db)
):
    return await school_service.update_school(db, school_id, data)


@router.delete("/{school_id}", response_model=MessageResponse)
async def delete_school(school_id: EightDigitId, db: AsyncSession = Depends(get_db)):
    await school_service.delete_school(db, school_id)
    return MessageResponse(detail=f"School {school_id} deleted")
