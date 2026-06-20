from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models.database import init_db
from .api import empire, agents, proposals, events, ws, court, chronicle, save
from .core.scheduler import setup_scheduler
from .core.save_watcher import watcher_manager, _process_saved_file
from .config import STELLARIS_SAVE_DIR
import asyncio
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    setup_scheduler()

    # 启动存档监控（如果目录存在）
    watcher_manager.set_handler(_process_saved_file)
    watcher_manager.set_loop(asyncio.get_event_loop())
    if STELLARIS_SAVE_DIR and os.path.isdir(STELLARIS_SAVE_DIR):
        try:
            watcher_manager.start(STELLARIS_SAVE_DIR)
            print(f"[Watcher] 监控目录: {STELLARIS_SAVE_DIR}")
        except Exception as e:
            print(f"[Watcher] 启动失败: {e}")

    yield

    watcher_manager.stop()


app = FastAPI(title="群星AI智囊团 API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:8080"], allow_methods=["*"], allow_headers=["*"])

app.include_router(empire.router)
app.include_router(agents.router)
app.include_router(proposals.router)
app.include_router(events.router)
app.include_router(ws.router)
app.include_router(court.router)
app.include_router(chronicle.router)
app.include_router(save.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
