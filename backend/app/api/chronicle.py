import json
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, union_all
from ..models.database import get_db
from ..models.agent_models import Proposal, EventLog, CoordinationTask, CourtSession

router = APIRouter(prefix="/api/chronicle", tags=["chronicle"])


@router.get("/")
async def get_chronicle(limit: int = 50, db: AsyncSession = Depends(get_db)):
    """聚合所有帝国大事记"""
    entries = []

    # 事件日志
    result = await db.execute(select(EventLog).order_by(EventLog.created_at.desc()).limit(limit))
    for e in result.scalars().all():
        entries.append({
            "type": "event",
            "subtype": e.event_type,
            "title": e.title,
            "description": e.description,
            "agent_id": e.agent_id,
            "time": e.created_at.isoformat() if e.created_at else None,
        })

    # 审批提议
    result = await db.execute(select(Proposal).order_by(Proposal.created_at.desc()).limit(limit))
    for p in result.scalars().all():
        entries.append({
            "type": "proposal",
            "subtype": p.status,
            "title": p.title,
            "description": p.description,
            "agent_id": p.agent_id,
            "cost": p.cost,
            "status": p.status,
            "time": p.created_at.isoformat() if p.created_at else None,
        })

    # 协调任务
    result = await db.execute(select(CoordinationTask).order_by(CoordinationTask.created_at.desc()).limit(limit))
    for c in result.scalars().all():
        entries.append({
            "type": "coordination",
            "subtype": c.status,
            "title": f"{c.from_agent} ↔ {c.to_agent} 协商",
            "description": c.issue,
            "agent_id": c.from_agent,
            "result": c.response_to,
            "status": c.status,
            "time": c.created_at.isoformat() if c.created_at else None,
        })

    # 朝会
    result = await db.execute(select(CourtSession).order_by(CourtSession.created_at.desc()).limit(limit))
    for cs in result.scalars().all():
        ts = json.loads(cs.transcript) if cs.transcript else []
        entries.append({
            "type": "court",
            "subtype": cs.status,
            "title": "帝国朝会",
            "description": f"共 {len(ts)} 条发言 · 状态: {cs.status}",
            "agent_id": "system",
            "session_id": cs.id,
            "time": cs.created_at.isoformat() if cs.created_at else None,
        })

    # 按时间排序
    entries.sort(key=lambda x: x["time"] or "", reverse=True)
    return entries[:limit]
