"""
OCR CCCD/CMND System — Standalone Launcher
Mở server FastAPI + tự động mở trình duyệt
"""
import os
import sys
import time
import socket
import threading
import webbrowser
import subprocess

# ── Configure console UTF-8 encoding on Windows ──
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── Fix OpenMP conflict (MUST be before torch import) ──
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

# ── Resolve base directory (works both in source and in EXE) ──
if getattr(sys, 'frozen', False):
    # Running as PyInstaller EXE
    BASE_DIR = os.path.dirname(sys.executable)
    # Tell the app where bundled data lives
    sys._MEIPASS_BASE = sys._MEIPASS if hasattr(sys, '_MEIPASS') else BASE_DIR
else:
    # Running from source
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Add source dir to path ──
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ── Prefer live app modules from disk if present (allows hot-updates without recompiling) ──
import importlib.machinery

class DiskAppFinder:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.finder = importlib.machinery.PathFinder()

    def find_spec(self, fullname, path=None, target=None):
        if fullname == "app" or fullname.startswith("app."):
            search_path = path if path is not None else [self.root_dir]
            spec = self.finder.find_spec(fullname, search_path, target)
            if spec is not None:
                return spec
        return None

app_disk_dir = os.path.join(BASE_DIR, "app")
if os.path.isdir(app_disk_dir):
    sys.meta_path.insert(0, DiskAppFinder(BASE_DIR))

HOST = "127.0.0.1"

def free_port(port: int = 8000, max_attempts: int = 3) -> bool:
    """Tự động kiểm tra và giải phóng cổng nếu có tiến trình chiếm dụng."""
    my_pid = os.getpid()
    for _ in range(max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            if s.connect_ex((HOST, port)) != 0:
                return True
        if sys.platform.startswith("win"):
            try:
                cmd = f'netstat -ano -p tcp | findstr :{port}'
                out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
                for line in out.strip().splitlines():
                    if "LISTENING" in line:
                        parts = line.strip().split()
                        pid = int(parts[-1])
                        if pid != my_pid and pid > 0:
                            subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        time.sleep(0.5)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex((HOST, port)) != 0

def find_available_port(start_port: int = 8000) -> int:
    if free_port(start_port):
        return start_port
    for p in [8001, 8002, 8080]:
        if free_port(p):
            return p
    return start_port

PORT = find_available_port(8000)
URL  = f"http://{HOST}:{PORT}"

BANNER = f"""
╔══════════════════════════════════════════════════════════╗
║    AI OCR · Nhận diện CCCD & CMND                       ║
║    Samsung Innovation Campus — Capstone Project 2026     ║
╠══════════════════════════════════════════════════════════╣
║  🌐  Địa chỉ : {URL:<43}║
║  📖  Swagger : {URL}/docs{'':<34}║
║  📁  Dữ liệu : {BASE_DIR:<43}║
╚══════════════════════════════════════════════════════════╝
  Nhấn Ctrl+C để tắt hệ thống
"""

def wait_then_open_browser():
    """Wait for server to be up, then open browser."""
    for _ in range(30):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex((HOST, PORT)) == 0:
                time.sleep(0.5)
                webbrowser.open(URL)
                return
        time.sleep(0.5)

def main():
    print(BANNER)

    # Start browser opener in background thread
    t = threading.Thread(target=wait_then_open_browser, daemon=True)
    t.start()

    # Start uvicorn
    import uvicorn
    from app.main import app as fastapi_app
    uvicorn.run(
        fastapi_app,
        host=HOST,
        port=PORT,
        reload=False,
        workers=1,
        log_level="info",
        access_log=True,
    )

if __name__ == "__main__":
    main()
