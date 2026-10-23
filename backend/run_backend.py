import os
import sys

# Ensure KMP_DUPLICATE_LIB_OK is set before importing torch or cv2
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
