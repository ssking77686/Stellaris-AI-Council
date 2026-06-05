"""
存档目录监控器。

使用 watchdog 监控《群星》存档目录，检测 .sav 文件变化后自动解析。
通过 asyncio.run_coroutine_threadsafe 将 watchdog 线程桥接到 FastAPI 事件循环。
"""

import asyncio
import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Awaitable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class SaveFileHandler(FileSystemEventHandler):
    """防抖文件事件处理器。

    群星保存存档时会多次写入同一个文件（zip 分块写入），
    用 2 秒防抖避免重复触发。
    """

    def __init__(self, callback: Callable[[str], None], debounce_sec: float = 2.0):
        self.callback = callback
        self.debounce_sec = debounce_sec
        self._pending: dict[str, float] = {}
        self._timer_handle: threading.Timer | None = None

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".sav"):
            self._schedule(event.src_path)

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".sav"):
            self._schedule(event.src_path)

    def on_moved(self, event):
        if not event.is_directory and event.dest_path.endswith(".sav"):
            self._schedule(event.dest_path)

    def _schedule(self, path: str):
        self._pending[path] = time.time()
        if self._timer_handle:
            self._timer_handle.cancel()
        self._timer_handle = threading.Timer(self.debounce_sec, self._fire)
        self._timer_handle.start()

    def _fire(self):
        pending = self._pending
        self._pending = {}
        self._timer_handle = None
        if pending:
            latest = max(pending.items(), key=lambda x: x[1])
            self.callback(latest[0])


class SaveWatcherManager:
    """存档监控管理器（模块级单例）。"""

    def __init__(self):
        self.observer: Observer | None = None
        self.watch_dir: str = ""
        self.is_running: bool = False
        self.last_detection: str = ""
        self.last_path: str = ""
        self._loop: asyncio.AbstractEventLoop | None = None
        self._async_handler: Callable[[str], Awaitable[None]] | None = None

    def set_handler(self, handler: Callable[[str], Awaitable[None]]):
        self._async_handler = handler

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    def start(self, directory: str):
        self.stop()
        path = os.path.expandvars(os.path.expanduser(directory))
        if not os.path.isdir(path):
            raise FileNotFoundError(f"存档目录不存在: {path}")
        self.watch_dir = path
        handler = SaveFileHandler(self._on_file_stable)
        self.observer = Observer()
        self.observer.schedule(handler, path, recursive=False)
        self.observer.start()
        self.is_running = True

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=5.0)
            self.observer = None
        self.is_running = False
        self.last_detection = ""

    def status(self) -> dict:
        return {
            "running": self.is_running,
            "directory": self.watch_dir,
            "last_detection": self.last_detection,
            "last_path": self.last_path,
        }

    def _on_file_stable(self, path: str):
        """文件稳定后的回调（watchdog 线程）。"""
        self.last_detection = time.strftime("%H:%M:%S")
        self.last_path = path
        if self._loop and self._async_handler:
            coro = self._async_handler(path)
            asyncio.run_coroutine_threadsafe(coro, self._loop)


# 模块级单例
watcher_manager = SaveWatcherManager()


async def _process_saved_file(path: str):
    """处理监控到的新存档文件。在事件循环中运行。"""
    from ..models.database import async_session
    from ..models.empire import EmpireState, SaveData
    from .save_parser import parse_save
    from ..api.ws import manager as ws_manager
    from sqlalchemy import select

    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError as e:
        print(f"[Watcher] 无法读取存档: {path} — {e}")
        return

    result = parse_save(data)
    if not result["parsed"]:
        print(f"[Watcher] 解析失败: {path} — {result.get('error', '?')}")
        return

    filename = os.path.basename(path)

    try:
        async with async_session() as db:
            # 同步到 EmpireState
            empire_data = result.get("empire", {})
            if empire_data:
                existing = await db.execute(select(EmpireState).where(EmpireState.id == 1))
                empire = existing.scalar_one_or_none()
                if not empire:
                    empire = EmpireState(id=1)
                    db.add(empire)

                field_map = {
                    "name": "name", "date": "game_date",
                    "energy_credits": "energy_credits", "minerals": "minerals", "food": "food",
                    "consumer_goods": "consumer_goods", "alloys": "alloys",
                    "influence": "influence", "unity": "unity",
                    "energy_income": "energy_income", "energy_expense": "energy_expense",
                    "mineral_income": "mineral_income", "trade_value": "trade_value",
                    "fleet_power": "fleet_power", "naval_capacity": "naval_capacity",
                    "naval_usage": "naval_usage", "starbase_count": "starbase_count",
                    "army_count": "army_count",
                    "physics_research": "physics_research", "society_research": "society_research",
                    "engineering_research": "engineering_research",
                    "current_tech": "current_tech", "tech_progress": "tech_progress",
                    "population": "population", "stability": "stability",
                    "empire_sprawl": "empire_sprawl", "sprawl_cap": "sprawl_cap",
                    "planet_count": "planet_count", "researched_techs": "researched_techs",
                    "total_ships": "total_ships", "war_status": "war_status",
                    "subject_count": "subject_count", "rival_count": "rival_count",
                    "species_count": "species_count", "planets_summary": "planets_summary",
                }
                for pk, attr in field_map.items():
                    if pk in empire_data:
                        setattr(empire, attr, empire_data[pk])
                for rk, rv in result.get("resources", {}).items():
                    if hasattr(empire, rk):
                        setattr(empire, rk, rv)

                empire.last_save_path = path
                empire.last_save_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 保存完整数据到 SaveData
            record = SaveData(
                save_name=filename,
                game_date=result["empire"].get("date", ""),
                empire_name=result["empire"].get("name", ""),
                planets_json=json.dumps(
                    [_d(p) for p in result.get("planets", [])], ensure_ascii=False
                ),
                fleets_json=json.dumps(
                    [_d(f) for f in result.get("fleets", [])], ensure_ascii=False
                ),
                techs_json=json.dumps(result.get("technologies", []), ensure_ascii=False),
                diplomacy_json=json.dumps(result.get("diplomacy", {}), ensure_ascii=False),
                leaders_json=json.dumps(
                    [_d(l) for l in result.get("leaders", [])], ensure_ascii=False
                ),
                empire_json=json.dumps(result.get("empire", {}), ensure_ascii=False),
            )
            db.add(record)
            await db.commit()

        # WebSocket 通知
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

        await ws_manager.notify("save_updated", {
            "save_name": filename,
            "game_date": result["empire"].get("date", ""),
            "empire_name": result["empire"].get("name", ""),
            "summary": {
                "energy": e.get("energy_credits", 0),
                "minerals": e.get("minerals", 0),
                "alloys": e.get("alloys", 0),
                "fleet_power": e.get("fleet_power", 0),
                "planets": len(result.get("planets", [])),
                "techs": e.get("researched_techs", 0),
                "pops": e.get("population", 0),
            },
            "alerts": alerts,
            "parsed_at": datetime.now().isoformat(),
        })

        print(f"[Watcher] 存档已解析: {filename} · {result['empire'].get('date', '')}")

    except Exception as exc:
        print(f"[Watcher] 数据库错误: {exc}")


def _d(obj) -> dict:
    """安全将对象转为 dict。"""
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
    return obj
