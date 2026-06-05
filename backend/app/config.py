import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")  # deepseek-fast

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./stellaris.db")

# Stellaris 存档目录（自动检测）
_default_save_dir = os.path.expandvars(
    r"%USERPROFILE%\Documents\Paradox Interactive\Stellaris\save games"
) if os.name == "nt" else os.path.expanduser(
    "~/.local/share/Paradox Interactive/Stellaris/save games"
)
STELLARIS_SAVE_DIR = os.getenv("STELLARIS_SAVE_DIR", _default_save_dir)
