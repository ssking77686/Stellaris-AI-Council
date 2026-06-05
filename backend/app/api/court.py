import uuid
import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.database import get_db
from ..models.agent_models import CourtSession
from ..core.court_orchestrator import run_court_session
from datetime import datetime

router = APIRouter(prefix="/api/court", tags=["court"])

active_sessions: dict[str, asyncio.Task] = {}


@router.post("/start")
async def start_court(db: AsyncSession = Depends(get_db)):
    """召开朝会"""
    # 检查是否有进行中的朝会
    result = await db.execute(
        select(CourtSession).where(CourtSession.status.in_(["opening", "reporting", "discussing", "closing"]))
    )
    ongoing = result.scalar_one_or_none()
    if ongoing:
        raise HTTPException(400, f"已有朝会进行中: {ongoing.id} (状态: {ongoing.status})")

    session = CourtSession(id=str(uuid.uuid4())[:12], status="pending")
    db.add(session)
    await db.commit()

    # 异步启动朝会
    task = asyncio.create_task(run_court_session(session.id))
    active_sessions[session.id] = task

    return {"session_id": session.id, "status": "started"}


@router.get("/current")
async def current_court(db: AsyncSession = Depends(get_db)):
    """获取当前进行中的朝会"""
    result = await db.execute(
        select(CourtSession).where(CourtSession.status.in_(["opening", "reporting", "discussing", "closing", "pending"]))
        .order_by(CourtSession.created_at.desc()).limit(1)
    )
    session = result.scalar_one_or_none()
    if not session:
        return {"session": None}
    return {
        "session": {
            "id": session.id,
            "status": session.status,
            "transcript": json.loads(session.transcript) if session.transcript else [],
            "created_at": session.created_at.isoformat() if session.created_at else None,
        }
    }


@router.get("/history")
async def court_history(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """获取朝会历史"""
    result = await db.execute(
        select(CourtSession).where(CourtSession.status == "closed")
        .order_by(CourtSession.created_at.desc()).limit(limit)
    )
    sessions = result.scalars().all()
    return [{"id": s.id, "status": s.status, "transcript": json.loads(s.transcript) if s.transcript else [],
             "created_at": s.created_at.isoformat() if s.created_at else None} for s in sessions]
