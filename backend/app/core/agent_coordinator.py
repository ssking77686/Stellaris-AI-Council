import json
import re
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.database import get_db
from ..models.agent_models import CoordinationTask
from ..agents.base import AGENTS, get_agent_prompt
from ..core.agent_engine import call_agent
from ..core.empire_simulator import get_empire


def parse_coordination(text: str) -> list[dict]:
    """解析 [COORDINATE:agent_id] 标记，返回协调请求列表"""
    pattern = r'\[COORDINATE:(\w+)\](.*?)\[/COORDINATE\]'
    results = []
    for match in re.finditer(pattern, text, re.DOTALL):
        results.append({"target_agent": match.group(1), "issue": match.group(2).strip()})
    return results


async def create_coordination(from_agent: str, to_agent: str, issue: str, db: AsyncSession) -> CoordinationTask:
    task = CoordinationTask(
        id=str(uuid.uuid4())[:12],
        from_agent=from_agent,
        to_agent=to_agent,
        issue=issue,
        status="pending",
        created_at=datetime.utcnow(),
    )
    db.add(task)
    await db.commit()
    return task


async def execute_coordination(task_id: str, db: AsyncSession):
    """执行协调：让目标 Agent 评估议题并回复"""
    result = await db.execute(select(CoordinationTask).where(CoordinationTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        return None

    if task.to_agent not in AGENTS:
        task.status = "failed"
        task.result = json.dumps({"error": f"Agent {task.to_agent} not found"})
        await db.commit()
        return task

    empire = await get_empire(db)
    prompt = get_agent_prompt(task.to_agent, empire.to_dict())
    message = f"【协调请求 — 来自{AGENTS.get(task.from_agent, {}).get('role_name', task.from_agent)}】\n议题：{task.issue}\n请就此议题给出你的专业评估和建议。"

    result_data = await call_agent(prompt, message)
    task.response_to = result_data["text"]
    task.result = json.dumps({"from_response": task.issue, "to_response": result_data["text"], "proposals": result_data.get("proposals", [])}, ensure_ascii=False)
    task.status = "resolved"
    task.resolved_at = datetime.utcnow()
    await db.commit()
    return task
