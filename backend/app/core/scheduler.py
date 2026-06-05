from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.database import async_session
from ..core.empire_simulator import get_empire, tick_empire, trigger_random_event
from ..api.ws import manager

scheduler = AsyncIOScheduler()


async def _tick_and_notify():
    """推进游戏时间并广播状态更新"""
    async with async_session() as db:
        await tick_empire(db, 1)
        event = await trigger_random_event(db)
        empire = await get_empire(db)
        state = empire.to_dict()
        await manager.notify("empire_tick", {"state": state, "event": event})


async def _periodic_report():
    """定期生成帝国概要报告"""
    async with async_session() as db:
        empire = await get_empire(db)
        state = empire.to_dict()
        # 生成简要摘要
        alerts = []
        if state.get("energy_credits", 0) < 500:
            alerts.append("能量币储备偏低")
        if state.get("alloys", 0) < 50:
            alerts.append("合金库存不足")
        if state.get("stability", 100) < 60:
            alerts.append("帝国稳定度下降")
        report = {
            "date": state.get("game_date"),
            "energy": state.get("energy_credits"),
            "minerals": state.get("minerals"),
            "fleet_power": state.get("fleet_power"),
            "alerts": alerts,
        }
        await manager.notify("periodic_report", report)


def setup_scheduler():
    """配置定时任务"""
    # 每 60 秒推进 1 天游戏时间
    scheduler.add_job(_tick_and_notify, "interval", seconds=60, id="tick")
    # 每 300 秒（5 分钟）生成一次帝国报告
    scheduler.add_job(_periodic_report, "interval", seconds=300, id="report")
    scheduler.start()
