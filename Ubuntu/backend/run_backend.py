import os
import sys
import time
import socket
import subprocess

# Ensure UTF-8 streams and environment before any imports
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Add current directory to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def free_port(port: int = 8000, max_attempts: int = 3) -> bool:
    """Kiểm tra và tự động giải phóng cổng nếu có tiến trình zombie cũ chiếm dụng."""
    my_pid = os.getpid()
    
    for _ in range(max_attempts):
        is_busy = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                is_busy = True
        
        if not is_busy:
            return True
            
        print(f"[CỔNG {port}] Cổng đang bị chiếm dụng bởi tiến trình cũ. Đang tự động giải phóng...")
        if sys.platform.startswith("win"):
            try:
                cmd = f'netstat -ano -p tcp | findstr :{port}'
                out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
                for line in out.strip().splitlines():
                    if "LISTENING" in line:
                        parts = line.strip().split()
                        pid = int(parts[-1])
                        if pid != my_pid and pid > 0:
                            print(f"[GIẢI PHÓNG] Đang đóng tiến trình treo (PID: {pid})...")
                            subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        else:
            try:
                subprocess.run(f"fuser -k {port}/tcp", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        time.sleep(0.5)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) != 0

def find_available_port(start_port: int = 8000, candidates: list = None) -> int:
    """Đảm bảo luôn tìm được cổng khả dụng để uvicorn không bao giờ gặp WinError 10048."""
    if candidates is None:
        candidates = [8000, 8001, 8002, 8080]
    
    if free_port(start_port):
        return start_port
        
    for p in candidates:
        if free_port(p):
            print(f"[CỔNG THAY THẾ] Sử dụng cổng {p} thay thế cho cổng {start_port}.")
            return p
    return start_port

import uvicorn

if __name__ == "__main__":
    target_port = find_available_port(8000)
    print("=" * 60)
    print("  HỆ THỐNG OCR CĂN CƯỚC CÔNG DÂN & CHỨNG MINH NHÂN DÂN")
    print(f"  Khởi chạy Server Backend tại: http://localhost:{target_port}")
    print(f"  Tài liệu Swagger:            http://localhost:{target_port}/docs")
    print("=" * 60)
    uvicorn.run("app.main:app", host="0.0.0.0", port=target_port, reload=False, workers=1)
