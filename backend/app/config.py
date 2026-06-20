import os
from pathlib import Path
from dotenv import load_dotenv, set_key

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(ENV_FILE)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./stellaris.db")

# Stellaris 存档目录（自动检测）
_default_save_dir = os.path.expandvars(
    r"%USERPROFILE%\Documents\Paradox Interactive\Stellaris\save games"
) if os.name == "nt" else os.path.expanduser(
    "~/.local/share/Paradox Interactive/Stellaris/save games"
)
STELLARIS_SAVE_DIR = os.getenv("STELLARIS_SAVE_DIR", _default_save_dir)


def get_config() -> dict:
    """返回当前配置，API Key 仅展示后 4 位。"""
    key = DEEPSEEK_API_KEY
    masked = (key[:4] + "****" + key[-4:]) if len(key) > 8 else ("****" if key else "")
    return {
        "api_key_masked": masked,
        "base_url": DEEPSEEK_BASE_URL,
        "model": DEEPSEEK_MODEL,
    }


def set_config(api_key: str = "", base_url: str = "", model: str = "") -> dict:
    """更新配置并写入 .env 文件，同时更新模块级变量。"""
    global DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

    if api_key:
        DEEPSEEK_API_KEY = api_key
        set_key(str(ENV_FILE), "DEEPSEEK_API_KEY", api_key)
    if base_url:
        DEEPSEEK_BASE_URL = base_url
        set_key(str(ENV_FILE), "DEEPSEEK_BASE_URL", base_url)
    if model:
        DEEPSEEK_MODEL = model
        set_key(str(ENV_FILE), "DEEPSEEK_MODEL", model)

    return get_config()
