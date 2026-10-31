import os
import sys
import time
import socket
import subprocess

# Fix OpenMP duplicate runtime and thread pool conflicts on Windows before any imports
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

# Ensure UTF-8 streams on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add current directory to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def is_port_free(port: int) -> bool:
    """Kiểm tra cổng trong tích tắc (<0.02s) bằng socket kết nối thử."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.05)
        return s.connect_ex(("127.0.0.1", port)) != 0

def free_port(port: int = 8000) -> bool:
    """Tự động giải phóng cổng tức thì nếu có tiến trình chiếm dụng."""
    if is_port_free(port):
        return True

    print(f"[CỔNG {port}] Phát hiện cổng đang bị chiếm. Đang giải phóng tức thì...")
    my_pid = os.getpid()

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
    else:
        try:
            subprocess.run(f"fuser -k {port}/tcp", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    time.sleep(0.3)
    return is_port_free(port)

def find_available_port(start_port: int = 8000) -> int:
    """Luôn đảm bảo server tìm được cổng hoạt động mượt mà."""
    if free_port(start_port):
        return start_port

    for p in [8001, 8002, 8080]:
        if is_port_free(p):
            print(f"[CỔNG DỰ PHÒNG] Cổng {start_port} bận, tự động kích hoạt cổng {p}.")
            return p
    return start_port

if __name__ == "__main__":
    target_port = find_available_port(8000)
    print("=" * 60)
    print("  HỆ THỐNG OCR CĂN CƯỚC CÔNG DÂN & CHỨNG MINH NHÂN DÂN")
    print(f"  Khởi chạy Server Backend tại: http://localhost:{target_port}")
    print(f"  Tài liệu Swagger:            http://localhost:{target_port}/docs")
    print("=" * 60)

    import uvicorn
    from app.main import app as fastapi_app

    # Chạy in-process trực tiếp với app object, loại bỏ hoàn toàn nguy cơ deadlock từ multiprocessing
    uvicorn.run(
        fastapi_app,
        host="0.0.0.0",
        port=target_port,
        reload=False,
        log_level="info"
    )
