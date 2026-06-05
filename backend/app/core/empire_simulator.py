import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.empire import EmpireState


EMPIRES = ["泽恩共同体", "卡尔联盟", "联合殖民地", "神谕帝国"]
TECHS = ["先进激光武器", "护盾强化", "聚变反应堆", "殖民狂热", "星际贸易", "基因修饰",
         "量子计算", "暗物质探测", "生态模拟", "超空间导航", "轨道防御平台", "纳米修复"]
EVENTS = [
    ("海盗袭击", "贸易路线遭到海盗袭击，损失 20 能量币"),
    ("科技突破", "科学家在研究中取得了意外突破"),
    ("外交使团", "邻国派遣使团提出贸易协定"),
    ("太空异常", "探索舰发现了一处神秘的太空异常信号"),
    ("矿物发现", "采矿站在深空发现了一处富矿脉"),
    ("派系活动", "国内派系发起了一场政治运动"),
    ("难民潮", "邻国爆发冲突，大量难民涌入边境"),
    ("星系风暴", "一场能量风暴影响了超空间航道稳定性"),
]


async def get_empire(db: AsyncSession) -> EmpireState:
    result = await db.execute(select(EmpireState).where(EmpireState.id == 1))
    empire = result.scalar_one_or_none()
    if not empire:
        empire = EmpireState(id=1)
        db.add(empire)
        await db.commit()
    return empire


async def tick_empire(db: AsyncSession, days: int = 1):
    """推进帝国时间，更新资源"""
    empire = await get_empire(db)
    empire.energy_credits += (empire.energy_income - empire.energy_expense) * days
    empire.minerals += empire.mineral_income * days
    empire.game_date = advance_date(empire.game_date, days)
    await db.commit()


async def trigger_random_event(db: AsyncSession) -> dict | None:
    """随机触发事件，5% 概率"""
    if random.random() > 0.05:
        return None
    event = random.choice(EVENTS)
    empire = await get_empire(db)
    if event[0] == "海盗袭击":
        empire.energy_credits = max(0, empire.energy_credits - 20)
    await db.commit()
    return {"title": event[0], "description": event[1]}


def advance_date(date_str: str, days: int) -> str:
    y, m, d = map(int, date_str.split("."))
    d += days
    while d > 30:
        d -= 30
        m += 1
    while m > 12:
        m -= 12
        y += 1
    return f"{y:04d}.{m:02d}.{d:02d}"
