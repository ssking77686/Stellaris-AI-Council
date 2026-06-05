from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.database import get_db
from ..models.agent_models import Proposal

router = APIRouter(prefix="/api/proposals", tags=["proposals"])


@router.get("/")
async def list_proposals(status: str = "pending", db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Proposal).where(Proposal.status == status))
    return result.scalars().all()


@router.post("/{proposal_id}/approve")
async def approve(proposal_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Proposal).where(Proposal.id == proposal_id))
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(404, "Proposal not found")
    proposal.status = "approved"
    await db.commit()
    return {"status": "approved"}


@router.post("/{proposal_id}/reject")
async def reject(proposal_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Proposal).where(Proposal.id == proposal_id))
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(404, "Proposal not found")
    proposal.status = "rejected"
    await db.commit()
    return {"status": "rejected"}
