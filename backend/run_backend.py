import os
import sys

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

import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("  HỆ THỐNG OCR CĂN CƯỚC CÔNG DÂN & CHỨNG MINH NHÂN DÂN")
    print("  Khởi chạy Server Backend tại: http://localhost:8000")
    print("  Tài liệu Swagger:            http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, workers=1)
