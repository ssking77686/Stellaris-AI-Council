from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.database import get_db
from ..models.agent_models import EventLog

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/")
async def list_events(limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EventLog).order_by(EventLog.created_at.desc()).limit(limit)
    )
    return result.scalars().all()
