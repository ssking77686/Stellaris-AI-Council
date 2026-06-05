"""存档管理 API — 上传、监控控制、解析历史。"""
import json
import os
import uuid
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import get_db
from ..models.empire import EmpireState, SaveData
from ..core.save_parser import parse_save
from ..core.save_watcher import watcher_manager
from ..api.ws import manager

router = APIRouter(prefix="/api/save", tags=["save"])


class WatcherStartRequest(BaseModel):
    directory: str


# ═══════════════════════════════════════════════════
# 存档上传
# ═══════════════════════════════════════════════════

@router.post("/upload")
async def upload_save(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """上传并解析 Stellaris 存档。"""
    if not file.filename or not file.filename.endswith(".sav"):
        return {"error": "请上传 .sav 格式的群星存档文件"}

    data = await file.read()
    result = parse_save(data)

    if not result["parsed"]:
        return result

    await _sync_empire_state(result, file.filename, db)
    await _save_record(result, file.filename, db)

    # WebSocket 通知前端
    await manager.notify("save_updated", {
        "save_name": file.filename,
        "game_date": result["empire"].get("date", ""),
        "empire_name": result["empire"].get("name", ""),
        "summary": _build_summary(result),
        "alerts": _check_alerts(result),
        "parsed_at": datetime.now().isoformat(),
    })

    return result


# ═══════════════════════════════════════════════════
# 存档监控控制
# ═══════════════════════════════════════════════════

@router.get("/watcher/status")
async def get_watcher_status():
    return watcher_manager.status()


@router.post("/watcher/start")
async def start_watcher(req: WatcherStartRequest):
    directory = os.path.expandvars(req.directory)
    directory = os.path.expanduser(directory)
    if not os.path.isdir(directory):
        raise HTTPException(400, f"目录不存在: {directory}")

    watcher_manager.start(directory)
    return {"status": "started", "directory": directory}


@router.post("/watcher/stop")
async def stop_watcher():
    watcher_manager.stop()
    return {"status": "stopped"}


# ═══════════════════════════════════════════════════
# 解析历史
# ═══════════════════════════════════════════════════

@router.get("/history")
async def get_save_history(limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SaveData).order_by(desc(SaveData.parsed_at)).limit(limit)
    )
    records = result.scalars().all()
    return [r.to_dict() for r in records]


@router.get("/{save_id}/detail")
async def get_save_detail(save_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SaveData).where(SaveData.id == save_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(404, "存档记录不存在")

    return {
        "id": record.id,
        "save_name": record.save_name,
        "game_date": record.game_date,
        "empire_name": record.empire_name,
        "planets": json.loads(record.planets_json),
        "fleets": json.loads(record.fleets_json),
        "technologies": json.loads(record.techs_json),
        "diplomacy": json.loads(record.diplomacy_json),
        "leaders": json.loads(record.leaders_json),
        "empire": json.loads(record.empire_json),
        "parsed_at": str(record.parsed_at) if record.parsed_at else "",
    }


# ═══════════════════════════════════════════════════
# 内部辅助
# ═══════════════════════════════════════════════════

_FIELD_MAP = {
    "name": "name",
    "date": "game_date",
    "energy_credits": "energy_credits",
    "minerals": "minerals",
    "food": "food",
    "consumer_goods": "consumer_goods",
    "alloys": "alloys",
    "influence": "influence",
    "unity": "unity",
    "energy_income": "energy_income",
    "mineral_income": "mineral_income",
    "fleet_power": "fleet_power",
    "naval_capacity": "naval_capacity",
    "naval_usage": "naval_usage",
    "starbase_count": "starbase_count",
    "physics_research": "physics_research",
    "society_research": "society_research",
    "engineering_research": "engineering_research",
    "current_tech": "current_tech",
    "tech_progress": "tech_progress",
    "population": "population",
    "stability": "stability",
    "empire_sprawl": "empire_sprawl",
    "sprawl_cap": "sprawl_cap",
    "planet_count": "planet_count",
    "total_ships": "total_ships",
    "war_status": "war_status",
    "subject_count": "subject_count",
    "rival_count": "rival_count",
    "species_count": "species_count",
    "planets_summary": "planets_summary",
}


async def _sync_empire_state(result: dict, filename: str, db: AsyncSession):
    """将解析结果同步到 EmpireState 表（单行，id=1）。"""
    empire_data = result.get("empire", {})
    if not empire_data:
        return

    existing = await db.execute(select(EmpireState).where(EmpireState.id == 1))
    empire = existing.scalar_one_or_none()
    if not empire:
        empire = EmpireState(id=1)
        db.add(empire)

    for parse_key, model_attr in _FIELD_MAP.items():
        if parse_key in empire_data:
            setattr(empire, model_attr, empire_data[parse_key])

    # 资源也映射
    resources = result.get("resources", {})
    for key, val in resources.items():
        if hasattr(empire, key):
            setattr(empire, key, val)

    empire.last_save_path = filename
    empire.last_save_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 邻居帝国数据
    neighbors = result.get("neighbors", [])
    if neighbors:
        empire.neighbors_json = json.dumps(neighbors, ensure_ascii=False)

    # 完整帝国数据存为 JSON（供 AI 提示使用）
    empire.planets_summary = result.get("empire", {}).get("planets_summary", "")

    await db.commit()


async def _save_record(result: dict, filename: str, db: AsyncSession):
    """保存完整解析数据到 SaveData 表。"""
    record = SaveData(
        save_name=filename,
        game_date=result["empire"].get("date", ""),
        empire_name=result["empire"].get("name", ""),
        planets_json=json.dumps(
            [_planet_to_dict(p) for p in result.get("planets", [])],
            ensure_ascii=False,
        ),
        fleets_json=json.dumps(
            [_fleet_to_dict(f) for f in result.get("fleets", [])],
            ensure_ascii=False,
        ),
        techs_json=json.dumps(result.get("technologies", []), ensure_ascii=False),
        diplomacy_json=json.dumps(result.get("diplomacy", {}), ensure_ascii=False),
        leaders_json=json.dumps(
            [_leader_to_dict(l) for l in result.get("leaders", [])],
            ensure_ascii=False,
        ),
        empire_json=json.dumps(result.get("empire", {}), ensure_ascii=False),
    )
    db.add(record)
    await db.commit()


def _build_summary(result: dict) -> dict:
    """构建 WebSocket 推送的摘要。"""
    e = result.get("empire", {})
    return {
        "energy": e.get("energy_credits", 0),
        "minerals": e.get("minerals", 0),
        "alloys": e.get("alloys", 0),
        "fleet_power": e.get("fleet_power", 0),
        "planets": e.get("planet_count", len(result.get("planets", []))),
        "techs": e.get("researched_techs", len(result.get("technologies", []))),
        "pops": e.get("population", 0),
    }


def _check_alerts(result: dict) -> list[str]:
    """基于存档数据生成预警。"""
    alerts = []
    e = result.get("empire", {})
    if e.get("alloys", 100) < 50:
        alerts.append("合金库存极低")
    if e.get("energy_credits", 0) < 100:
        alerts.append("能量币严重不足")
    if e.get("food", 0) < 0:
        alerts.append("食物产量为负")
    if e.get("stability", 100) < 40:
        alerts.append("帝国稳定度危险")
    if e.get("naval_usage", 0) > e.get("naval_capacity", 1):
        alerts.append("海军容量超出上限")
    return alerts


def _planet_to_dict(p) -> dict:
    if hasattr(p, "__dict__"):
        d = {k: v for k, v in p.__dict__.items() if not k.startswith("_")}
        return d
    return p


def _fleet_to_dict(f) -> dict:
    if hasattr(f, "__dict__"):
        return {k: v for k, v in f.__dict__.items() if not k.startswith("_")}
    return f


def _leader_to_dict(l) -> dict:
    if hasattr(l, "__dict__"):
        return {k: v for k, v in l.__dict__.items() if not k.startswith("_")}
    return l
