"""
群星AI智囊团 — 一键启动器

用法:
    python start.py            # 启动全部服务
    python start.py --backend  # 仅启动后端
    python start.py --frontend # 仅启动前端
"""

import subprocess
import sys
import time
import webbrowser
import os
import threading
from pathlib import Path

# 修复 Windows 终端编码问题
if os.name == "nt":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "stellaris-command-center"

BACKEND_PORT = 8001
FRONTEND_PORT = 5173

# 颜色标记 (ANSI)
C = {"reset": "\033[0m", "green": "\033[92m", "yellow": "\033[93m",
     "cyan": "\033[96m", "red": "\033[91m", "bold": "\033[1m"}

def safe(msg: str) -> str:
    """编码安全：替换无法被终端显示的字符。"""
    try:
        msg.encode(sys.stdout.encoding or "utf-8")
        return msg
    except (UnicodeEncodeError, UnicodeDecodeError):
        return msg.encode("ascii", errors="replace").decode("ascii")

def log(tag: str, msg: str, color: str = "cyan"):
    try:
        print(f"{C.get(color, '')}[{tag}]{C['reset']} {safe(msg)}")
    except Exception:
        print(f"[{tag}] {msg}")

def _find_nodejs() -> str | None:
    """在 Windows 上自动定位 Node.js 安装路径。"""
    candidates = [
        r"C:\Program Files\nodejs",
        r"C:\Program Files (x86)\nodejs",
        os.path.expandvars(r"%APPDATA%\..\Local\pnpm"),
        os.path.expandvars(r"%LOCALAPPDATA%\pnpm"),
    ]
    # 也检查 npm 全局安装的 node
    try:
        result = subprocess.run(["where", "node"], capture_output=True, text=True, shell=True, timeout=5)
        if result.returncode == 0:
            node_path = result.stdout.strip().split("\n")[0]
            return str(Path(node_path).parent)
    except Exception:
        pass
    for c in candidates:
        if os.path.isdir(c) and os.path.isfile(os.path.join(c, "node.exe")):
            return c
    return None

def _setup_path():
    """确保 Node.js 在 PATH 中。"""
    node_dir = _find_nodejs()
    if node_dir and node_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = node_dir + os.pathsep + os.environ.get("PATH", "")
        return True
    return node_dir is not None

def check_command(cmd: str, name: str) -> bool:
    try:
        subprocess.run(cmd, capture_output=True, shell=True, timeout=10)
        return True
    except Exception:
        log("check", f"Not found: {name}", "red")
        return False

def run_process(cmd: list[str], cwd: Path, name: str, env: dict = None):
    try:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        proc = subprocess.Popen(
            cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", env=merged_env,
            bufsize=1, creationflags=flags,
        )
        for line in proc.stdout:
            line = line.rstrip()
            if line:
                log(name, line)
        proc.wait()
    except Exception as e:
        log(name, f"Error: {e}", "red")

def start_backend():
    log("Backend", "Starting...", "yellow")
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app",
           "--port", str(BACKEND_PORT), "--host", "0.0.0.0"]
    t = threading.Thread(target=run_process, args=(cmd, BACKEND_DIR, "Backend"), daemon=True)
    t.start()
    for _ in range(20):
        time.sleep(1)
        try:
            import urllib.request
            urllib.request.urlopen(f"http://localhost:{BACKEND_PORT}/api/health", timeout=3)
            log("Backend", f"Ready -> http://localhost:{BACKEND_PORT}", "green")
            return True
        except Exception:
            pass
    log("Backend", "Start timeout", "red")
    return False

def start_frontend():
    log("Frontend", "Starting...", "yellow")
    npm = "pnpm.cmd" if os.name == "nt" else "pnpm"
    cmd = [npm, "dev", "--port", str(FRONTEND_PORT)]
    t = threading.Thread(target=run_process, args=(cmd, FRONTEND_DIR, "Frontend"), daemon=True)
    t.start()
    for _ in range(25):
        time.sleep(1)
        try:
            import urllib.request
            urllib.request.urlopen(f"http://localhost:{FRONTEND_PORT}", timeout=3)
            log("Frontend", f"Ready -> http://localhost:{FRONTEND_PORT}", "green")
            return True
        except Exception:
            pass
    log("Frontend", "Start timeout", "red")
    return False

def install_deps():
    # Backend deps
    pip_lock = BACKEND_DIR / ".deps_installed"
    if not pip_lock.exists():
        log("Deps", "Installing Python packages...", "yellow")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            cwd=str(BACKEND_DIR), capture_output=True, text=True,
        )
        if result.returncode == 0:
            pip_lock.touch()
            log("Deps", "Python packages installed", "green")
        else:
            log("Deps", f"Failed:\n{result.stderr[-300:]}", "red")
            return False

    # Frontend deps
    if not (FRONTEND_DIR / "node_modules").exists():
        log("Deps", "Installing Node packages (pnpm install)...", "yellow")
        npm = "pnpm.cmd" if os.name == "nt" else "pnpm"
        result = subprocess.run(
            [npm, "install"], cwd=str(FRONTEND_DIR),
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            (FRONTEND_DIR / "node_modules").mkdir(parents=True, exist_ok=True)
            (FRONTEND_DIR / "node_modules" / ".deps_installed").touch()
            log("Deps", "Node packages installed", "green")
        else:
            log("Deps", f"Failed:\n{result.stderr[-300:]}", "red")
            return False

    return True

def main():
    print(f"\n  === Stellaris AI Brain Trust ===\n")

    # 自动修复 Windows PATH
    if os.name == "nt":
        _setup_path()

    run_backend = "--frontend" not in sys.argv
    run_frontend = "--backend" not in sys.argv

    # Check environment
    if run_backend:
        if not check_command(f'"{sys.executable}" --version', "Python"):
            sys.exit(1)
    if run_frontend:
        npm = "pnpm.cmd" if os.name == "nt" else "pnpm"
        if not check_command(f'{npm} --version', "pnpm (Node.js)"):
            sys.exit(1)

    # Install
    if not install_deps():
        log("Start", "Dependency install failed. Run manually:")
        print(f"  cd backend && pip install -r requirements.txt")
        print(f"  cd stellaris-command-center && pnpm install")
        sys.exit(1)

    print()

    # Start services
    be_ok = fe_ok = True
    if run_backend:
        be_ok = start_backend()
    if run_frontend:
        fe_ok = start_frontend()

    print()
    if be_ok and fe_ok:
        log("Ready", "All services running", "green")
        print(f"  Dashboard:    http://localhost:{FRONTEND_PORT}")
        print(f"  Save Manager: http://localhost:{FRONTEND_PORT}/saves")
        print(f"  API Docs:     http://localhost:{BACKEND_PORT}/docs")
        print(f"  Press Ctrl+C to stop\n")
        webbrowser.open(f"http://localhost:{FRONTEND_PORT}")
    elif be_ok:
        log("Ready", "Backend running. Frontend: cd stellaris-command-center && pnpm dev", "yellow")
    elif fe_ok:
        log("Ready", "Frontend running. Backend: cd backend && python -m uvicorn app.main:app --port 8001", "yellow")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n  Stopped.\n")

if __name__ == "__main__":
    main()
