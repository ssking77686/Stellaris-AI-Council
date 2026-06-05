import json
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.database import async_session
from ..models.agent_models import CourtSession
from ..agents.base import AGENTS, get_agent_prompt
from ..core.agent_engine import call_agent
from ..core.empire_simulator import get_empire
from ..api.ws import manager

STAGE_ORDER = ["opening", "reporting", "discussing", "closing", "closed"]


async def _broadcast_speech(session_id: str, stage: str, agent_id: str, speaker: str, text: str):
    speech = {
        "session_id": session_id,
        "stage": stage,
        "agent_id": agent_id,
        "speaker": speaker,
        "text": text,
        "time": datetime.utcnow().isoformat(),
    }
    await manager.notify("court_speech", speech)
    return speech


async def _save_speeches(session_id: str, speeches: list):
    async with async_session() as db:
        result = await db.execute(select(CourtSession).where(CourtSession.id == session_id))
        session = result.scalar_one_or_none()
        if session:
            session.transcript = json.dumps(speeches, ensure_ascii=False)
            await db.commit()


async def run_court_session(session_id: str):
    """执行四阶段朝会"""
    speeches = []
    agenda_topics = ["帝国资源评估", "军事防御态势", "科研进展与路线", "外交形势分析", "内政稳定报告", "建造与殖民计划"]

    async with async_session() as db:
        empire = await get_empire(db)
        state = empire.to_dict()
        result = await db.execute(select(CourtSession).where(CourtSession.id == session_id))
        session = result.scalar_one_or_none()
        if not session:
            return

    # === 阶段一：开幕 ===
    session.status = "opening"
    await _update_session(session_id, "opening")
    opening_text = f"【帝国朝会 — {state.get('game_date', '?')}】\n诸臣就位。今日议题：{'、'.join(agenda_topics)}。按例，各司依次汇报。"
    speech = await _broadcast_speech(session_id, "opening", "system", "帝国皇帝", opening_text)
    speeches.append(speech)
    await asyncio.sleep(1)

    # === 阶段二：汇报 ===
    session.status = "reporting"
    await _update_session(session_id, "reporting")
    report_prompts = {
        "finance": "请就帝国财政状况做简短汇报（50字以内），包括能量币储备和经济展望。",
        "military": "请就军事态势做简短汇报（50字以内），包括舰队战力和边境防御。",
        "science": "请就科研进展做简短汇报（50字以内），包括关键科技和下一步方向。",
        "foreign": "请就外交形势做简短汇报（50字以内），包括联邦地位和周边关系。",
        "interior": "请就内政状况做简短汇报（50字以内），包括人口稳定度和派系动态。",
        "construction": "请就建造殖民进展做简短汇报（50字以内），包括在建项目和殖民机会。",
    }

    agent_order = ["finance", "military", "science", "foreign", "interior", "construction"]
    agent_reports = {}

    for agent_id in agent_order:
        if agent_id not in AGENTS:
            continue
        prompt = get_agent_prompt(agent_id, state)
        result_data = await call_agent(prompt, report_prompts.get(agent_id, "请汇报你的领域状况。"))
        agent_name = AGENTS[agent_id]["role_name"]
        speech = await _broadcast_speech(session_id, "reporting", agent_id, agent_name, result_data["text"])
        speeches.append(speech)
        agent_reports[agent_id] = result_data["text"]
        await asyncio.sleep(0.5)

    # === 阶段三：讨论 ===
    session.status = "discussing"
    await _update_session(session_id, "discussing")

    # 选出关键议题进行讨论
    discussion_topics = []
    if state.get("alloys", 0) < 100:
        discussion_topics.append("合金储备不足，需要军事大臣和建造大臣协调建设优先级")
    if state.get("border_tension") == "升高":
        discussion_topics.append("边境局势紧张，需要外交大臣和军事大臣讨论应对策略")
    if state.get("stability", 0) < 70:
        discussion_topics.append("帝国稳定度下降，需要内政大臣提出安抚方案")
    if not discussion_topics:
        discussion_topics.append("帝国当前运转平稳，请诸位大臣就未来发展各抒己见")

    discussion_round = 0
    for topic in discussion_topics[:2]:  # 最多讨论 2 个议题
        discussion_round += 1
        # 让相关度最高的大臣先发言
        first_agent = "finance"
        if "军事" in topic or "合金" in topic:
            first_agent = "military"
        elif "外交" in topic or "边境" in topic:
            first_agent = "foreign"
        elif "稳定" in topic:
            first_agent = "interior"

        if first_agent in AGENTS:
            prompt = get_agent_prompt(first_agent, state)
            context = f"【朝会讨论 · 第{discussion_round}轮】\n议题：{topic}\n此前汇报要点：{json.dumps(agent_reports, ensure_ascii=False)}\n请就此议题发表你的意见（80字以内）。"
            result_data = await call_agent(prompt, context)
            agent_name = AGENTS[first_agent]["role_name"]
            speech = await _broadcast_speech(session_id, "discussing", first_agent, agent_name, result_data["text"])
            speeches.append(speech)
            await asyncio.sleep(0.5)

        # 第二位大臣回应
        second_agent = "construction" if first_agent == "military" else "military" if first_agent == "foreign" else "finance"
        if second_agent in AGENTS:
            prompt = get_agent_prompt(second_agent, state)
            context = f"【朝会讨论 · 第{discussion_round}轮】\n议题：{topic}\n{AGENTS[first_agent]['role_name']}的发言：{speech['text']}\n请回应并补充你的观点（60字以内）。"
            result_data = await call_agent(prompt, context)
            agent_name = AGENTS[second_agent]["role_name"]
            speech = await _broadcast_speech(session_id, "discussing", second_agent, agent_name, result_data["text"])
            speeches.append(speech)
            await asyncio.sleep(0.5)

        # 如果还有余量，让皇帝做总结
        if discussion_round == 1:
            summary = await _broadcast_speech(session_id, "discussing", "system", "帝国皇帝",
                f"诸臣言之有理。关于「{topic}」的讨论到此，请建造大臣和财政大臣在朝会后拿出具体方案呈报。")
            speeches.append(summary)

    # === 阶段四：闭幕 ===
    session.status = "closing"
    await _update_session(session_id, "closing")
    closing_text = f"【朝会闭幕】\n今日朝会听取了 6 位大臣的汇报，讨论了 {len(discussion_topics[:2])} 项议题。决议：请相关部门在三日内提交具体执行方案。下次朝会定于一个月后召开。退朝。"
    speech = await _broadcast_speech(session_id, "closing", "system", "帝国皇帝", closing_text)
    speeches.append(speech)

    # 保存
    await _save_speeches(session_id, speeches)
    session.status = "closed"
    await _update_session(session_id, "closed")
    await manager.notify("court_closed", {"session_id": session_id, "total_speeches": len(speeches)})


async def _update_session(session_id: str, status: str):
    async with async_session() as db:
        result = await db.execute(select(CourtSession).where(CourtSession.id == session_id))
        session = result.scalar_one_or_none()
        if session:
            session.status = status
            await db.commit()
