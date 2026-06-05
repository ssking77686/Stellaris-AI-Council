import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from ..models.database import get_db
from ..models.agent_models import Conversation, CoordinationTask
from ..core.agent_engine import call_agent, call_agent_stream
from ..core.agent_coordinator import parse_coordination, create_coordination, execute_coordination
from ..core.empire_simulator import get_empire
from ..agents.base import get_agent_prompt, AGENTS
from ..api.ws import manager

router = APIRouter(prefix="/api/agents", tags=["agents"])


class ChatRequest(BaseModel):
    agent_id: str
    message: str


@router.get("/list")
async def list_agents():
    return [{"id": a["id"], "role_name": a["role_name"], "domain": a["domain"]} for a in AGENTS.values()]


@router.post("/chat")
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    if req.agent_id not in AGENTS:
        raise HTTPException(404, "Agent not found")
    empire = await get_empire(db)
    prompt = get_agent_prompt(req.agent_id, empire.to_dict())
    result = await call_agent(prompt, req.message)

    # 检测协调标记
    coord_requests = parse_coordination(result["text"])
    coord_results = []
    for cr in coord_requests:
        if cr["target_agent"] in AGENTS:
            task = await create_coordination(req.agent_id, cr["target_agent"], cr["issue"], db)
            resolved = await execute_coordination(task.id, db)
            coord_results.append({
                "id": task.id,
                "from": req.agent_id,
                "to": cr["target_agent"],
                "response": resolved.response_to if resolved else None,
            })
            await manager.notify("coordination", {
                "id": task.id, "from": req.agent_id, "to": cr["target_agent"],
                "issue": cr["issue"], "status": resolved.status if resolved else "failed",
            })

    return {"text": result["text"], "proposals": result["proposals"], "coordinations": coord_results}


@router.post("/coordinate")
async def coordinate(from_agent: str, to_agent: str, issue: str, db: AsyncSession = Depends(get_db)):
    """手动触发 Agent 间协调"""
    if from_agent not in AGENTS or to_agent not in AGENTS:
        raise HTTPException(404, "Agent not found")
    task = await create_coordination(from_agent, to_agent, issue, db)
    resolved = await execute_coordination(task.id, db)
    await manager.notify("coordination", {
        "id": task.id, "from": from_agent, "to": to_agent,
        "issue": issue, "status": resolved.status if resolved else "failed",
    })
    return {
        "id": task.id,
        "issue": issue,
        "from_response": resolved.response_to if resolved else None,
        "status": resolved.status if resolved else "failed",
    }


@router.get("/coordinations")
async def list_coordinations(limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CoordinationTask).order_by(CoordinationTask.created_at.desc()).limit(limit)
    )
    return result.scalars().all()


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    if req.agent_id not in AGENTS:
        raise HTTPException(404, "Agent not found")
    empire = await get_empire(db)
    prompt = get_agent_prompt(req.agent_id, empire.to_dict())

    async def generate():
        async for chunk in call_agent_stream(prompt, req.message):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
