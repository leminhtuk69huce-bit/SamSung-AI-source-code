import os
import sys
from pathlib import Path

# Fix OpenMP duplicate library runtime on Windows Conda
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# ── Path resolution: works in both source mode and PyInstaller EXE ──
if getattr(sys, 'frozen', False):
    EXE_DIR = Path(sys.executable).parent
    BASE_DIR = EXE_DIR
    BUNDLE_DIR = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else EXE_DIR
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    BUNDLE_DIR = BASE_DIR

STORAGE_DIR = BASE_DIR / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Ưu tiên thư mục tạm riêng biệt nếu người dùng yêu cầu, tránh rải rác
custom_temp = Path(r"E:\TEMPPPP\temp)))")
if custom_temp.exists():
    TEMP_DIR = custom_temp
else:
    TEMP_DIR = STORAGE_DIR / "temp"
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

import tempfile
tempfile.tempdir = str(TEMP_DIR)
os.environ["TEMP"] = str(TEMP_DIR)
os.environ["TMP"] = str(TEMP_DIR)


if getattr(sys, 'frozen', False):
    WORKSPACE_DIR = BASE_DIR
else:
    WORKSPACE_DIR = BASE_DIR.parent

# Database path
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/ocr_database.db")

# ── OCR & Hardware Settings ──
OCR_LANGUAGES = ["vi", "en"]
TARGET_IMAGE_WIDTH = 1280  # Optimized width for OCR inference

def _detect_hardware():
    """
    Tự động nhận diện phần cứng GPU RTX 4060 hoặc CPU.
    Hỗ trợ đường lui an toàn: Có thể chuyển sang CPU bằng cách đặt:
      - Biến môi trường OCR_GPU=false
      - Hoặc OCR_DEVICE=cpu
    """
    env_gpu = os.getenv("OCR_GPU")
    env_dev = os.getenv("OCR_DEVICE", "").strip().lower()

    # Đường lui: Ép về CPU theo cấu hình người dùng
    if env_dev == "cpu" or (env_gpu is not None and env_gpu.strip().lower() == "false"):
        return False, "CPU (Người dùng chỉ định chế độ an toàn)"

    # Ép về GPU nếu người dùng yêu cầu
    if env_dev in ("cuda", "gpu") or (env_gpu is not None and env_gpu.strip().lower() == "true"):
        return True, "NVIDIA GPU (Ép buộc qua biến môi trường)"

    # Mặc định: Tự động phát hiện GPU khả dụng
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            return True, f"NVIDIA GPU ({gpu_name})"
    except Exception:
        pass

    return False, "CPU (Mặc định)"

OCR_GPU, OCR_HARDWARE_INFO = _detect_hardware()

# Confidence thresholds
CONFIDENCE_HIGH = 0.85
CONFIDENCE_MEDIUM = 0.60

# API Settings
API_TITLE = "Hệ Thống OCR Căn Cước Công Dân & CMND API"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
Hệ thống nhận diện kí tự quang học (OCR) và trích xuất thông tin tự động 
từ bản scan/ảnh chụp CCCD (có chip/mã vạch) và CMND (9 số, 12 số).
Hỗ trợ upload ảnh, chụp trực tiếp qua Webcam máy tính, lưu trữ lịch sử và xuất báo cáo.
"""

# CORS Origins
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
    "*"  # Allow all for convenient multi-AI / local testing
]
