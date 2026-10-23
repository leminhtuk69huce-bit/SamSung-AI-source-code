import os
import sys
from pathlib import Path

# ── Path resolution: works in both source mode and PyInstaller EXE ──
if getattr(sys, 'frozen', False):
    # Running as EXE → use the directory containing OCR_CCCD.exe
    # (persistent: DB/storage survive between runs)
    EXE_DIR = Path(sys.executable).parent
    BASE_DIR = EXE_DIR
    # _MEIPASS is the temp bundle dir (read-only libs); use EXE_DIR for data
    BUNDLE_DIR = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else EXE_DIR
else:
    # Running from source
    BASE_DIR = Path(__file__).resolve().parent.parent
    BUNDLE_DIR = BASE_DIR

STORAGE_DIR = BASE_DIR / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

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

# OCR Settings
OCR_LANGUAGES = ["vi", "en"]
OCR_GPU = os.getenv("OCR_GPU", "false").lower() == "true"
TARGET_IMAGE_WIDTH = 1280  # Optimized width for OCR inference

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
