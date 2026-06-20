from fastapi import APIRouter
from pydantic import BaseModel
from ..config import get_config, set_config
from ..core.agent_engine import reload_client, test_connection

router = APIRouter(prefix="/api/config", tags=["config"])


class ConfigUpdate(BaseModel):
    api_key: str = ""
    base_url: str = ""
    model: str = ""


@router.get("")
async def get_current_config():
    return get_config()


@router.post("")
async def update_config(body: ConfigUpdate):
    result = set_config(
        api_key=body.api_key,
        base_url=body.base_url,
        model=body.model,
    )
    if body.api_key or body.base_url:
        reload_client(api_key=body.api_key, base_url=body.base_url)
    return {"status": "ok", "config": result}


@router.post("/test")
async def test_api_connection():
    result = await test_connection()
    return result
