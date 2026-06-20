import http.server
import socketserver
import os
import sys
import threading
import time
import webview

ASSET_DIR = ""
START_PORT = 8080
MAX_PORT = 8089
port = START_PORT


class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ASSET_DIR, **kwargs)

    def do_GET(self):
        file_path = self.translate_path(self.path)
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            super().do_GET()
        else:
            index = os.path.join(ASSET_DIR, "index.html")
            try:
                with open(index, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", len(content))
                self.end_headers()
                self.wfile.write(content)
            except FileNotFoundError:
                self.send_error(500, "SPA index.html missing — build may be corrupt")

    def log_message(self, format, *args):
        pass


def get_asset_dir():
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "www")
    from pathlib import Path
    return str(Path(__file__).resolve().parent / "www")


def find_port():
    """Try START_PORT through MAX_PORT, return first available."""
    global port
    for p in range(START_PORT, MAX_PORT + 1):
        try:
            s = socketserver.TCPServer(("127.0.0.1", p), SPAHandler)
            s.server_close()
            port = p
            return
        except OSError:
            continue
    # All ports busy
    import ctypes
    ctypes.windll.user32.MessageBoxW(0,
        f"端口 {START_PORT}-{MAX_PORT} 均被占用，无法启动。\n请关闭占用端口的程序后重试。",
        "银河帝国指挥中心 — 启动失败", 0x10)
    sys.exit(1)


def serve_forever(asset_dir):
    global ASSET_DIR
    ASSET_DIR = asset_dir
    with socketserver.TCPServer(("127.0.0.1", port), SPAHandler) as httpd:
        httpd.serve_forever()


def main():
    asset_dir = get_asset_dir()
    find_port()

    threading.Thread(target=serve_forever, args=(asset_dir,), daemon=True).start()
    time.sleep(0.3)

    webview.create_window(
        title="银河帝国指挥中心 — 群星AI智囊团",
        url=f"http://127.0.0.1:{port}",
        width=1280,
        height=820,
        min_size=(960, 600),
    )
    webview.start()


if __name__ == "__main__":
    main()
