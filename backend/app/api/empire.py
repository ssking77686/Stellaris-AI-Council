from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.database import get_db
from ..core.empire_simulator import get_empire, tick_empire, trigger_random_event

router = APIRouter(prefix="/api/empire", tags=["empire"])


@router.get("/state")
async def empire_state(db: AsyncSession = Depends(get_db)):
    empire = await get_empire(db)
    return empire.to_dict()


@router.post("/tick")
async def advance_time(days: int = 1, db: AsyncSession = Depends(get_db)):
    await tick_empire(db, days)
    event = await trigger_random_event(db)
    empire = await get_empire(db)
    return {"state": empire.to_dict(), "event": event}
