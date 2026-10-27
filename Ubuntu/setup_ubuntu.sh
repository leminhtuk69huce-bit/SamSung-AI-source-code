#!/usr/bin/env bash
# ==============================================================================
# SCRIPT TỰ ĐỘNG CÀI ĐẶT MÔI TRƯỜNG CHO HỆ ĐIỀU HÀNH UBUNTU / LINUX
# DỰ ÁN: AI OCR CĂN CƯỚC CÔNG DÂN & CHỨNG MINH NHÂN DÂN VIỆT NAM
# ==============================================================================

set -e

# Đổi thư mục làm việc về thư mục gốc của script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "======================================================================"
echo "  [AI OCR CCCD/CMND] BẮT ĐẦU CÀI ĐẶT HỆ THỐNG TRÊN UBUNTU / LINUX"
echo "======================================================================"

# 1. Kiểm tra Python 3
if ! command -v python3 &> /dev/null; then
    echo "[LỖI] Không tìm thấy python3! Vui lòng cài đặt Python 3.8+:"
    echo "      sudo apt update && sudo apt install -y python3 python3-pip python3-venv"
    exit 1
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "[OK] Đã tìm thấy Python: $PY_VER"

# 2. Cài đặt các thư viện hệ thống cần thiết (nếu có quyền sudo)
echo "[INFO] Kiểm tra các gói thư viện hệ thống bổ trợ (libgl1, libglib2.0-0, python3-venv)..."
if command -v sudo &> /dev/null && [ "$EUID" -ne 0 ]; then
    echo "  (Nếu được hỏi mật khẩu sudo, hãy nhập để cài đặt thư viện hệ thống Ubuntu)"
    sudo apt-get update -qq || true
    sudo apt-get install -y -qq python3-pip python3-venv libgl1 libglib2.0-0 >/dev/null 2>&1 || {
        echo "[CẢNH BÁO] Không thể tự động chạy apt-get (có thể do thiếu quyền sudo)."
        echo "Nếu gặp lỗi liên quan đến venv hoặc libGL, hãy tự chạy: sudo apt install -y python3-venv libgl1 libglib2.0-0"
    }
fi

# 3. Tạo môi trường ảo Python Virtualenv (Chuẩn Ubuntu 22.04 / 24.04 không dùng pip toàn cục)
if [ ! -d "venv" ]; then
    echo "[INFO] Đang khởi tạo môi trường ảo Python (venv)..."
    python3 -m venv venv || {
        echo "[LỖI] Không thể tạo venv! Hãy chạy lệnh sau trên terminal của bạn rồi chạy lại script này:"
        echo "      sudo apt install -y python3-venv"
        exit 1
    }
    echo "[OK] Đã tạo thư mục môi trường ảo venv thành công."
else
    echo "[INFO] Đã tồn tại môi trường ảo venv."
fi

# 4. Kích hoạt venv và nâng cấp pip
echo "[INFO] Kích hoạt venv và nâng cấp pip..."
source venv/bin/activate
pip install --upgrade pip -q

# 5. Cài đặt các thư viện Python từ requirements.txt
echo "[INFO] Đang cài đặt các thư viện AI OCR (FastAPI, PyTorch, EasyOCR, OpenCV, Pandas)..."
echo "       (Quá trình này có thể mất từ 1 - 3 phút tùy tốc độ mạng)"
pip install -r backend/requirements.txt -q

# 6. Kiểm tra nạp mô hình & thư viện
echo "[INFO] Kiểm tra nạp thử nghiệm các thư viện cốt lõi..."
python3 -c "import torch, easyocr, cv2, fastapi; print('[OK] Import thư viện AI thành công! PyTorch version:', torch.__version__)"

# 7. Cấp quyền thực thi cho các script chạy
chmod +x setup_ubuntu.sh run.sh test.sh 2>/dev/null || true

echo "======================================================================"
echo "🎉 CÀI ĐẶT THÀNH CÔNG HỆ THỐNG AI OCR TRÊN UBUNTU!"
echo "======================================================================"
echo "Cách khởi động ứng dụng:"
echo "  Cách 1 (Nhanh nhất):  ./run.sh"
echo "  Cách 2 (Thủ công):   source venv/bin/activate && python3 backend/run_backend.py"
echo "  Chạy kiểm thử:       ./test.sh"
echo ""
echo "Giao diện Web sẽ tự động mở hoặc truy cập tại: http://localhost:8000/demo"
echo "======================================================================"
