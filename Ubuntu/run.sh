#!/usr/bin/env bash
# ==============================================================================
# SCRIPT KHỞI CHẠY 1-CLICK CHO HỆ ĐIỀU HÀNH UBUNTU / LINUX
# DỰ ÁN: AI OCR CĂN CƯỚC CÔNG DÂN & CHỨNG MINH NHÂN DÂN VIỆT NAM
# ==============================================================================

# Đổi thư mục làm việc về thư mục chứa script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

# 1. Tự động kiểm tra môi trường ảo
if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
    echo "[INFO] Chưa tìm thấy môi trường ảo (venv). Hệ thống sẽ tự động chạy script cài đặt ban đầu..."
    chmod +x setup_ubuntu.sh 2>/dev/null || true
    ./setup_ubuntu.sh
    if [ $? -ne 0 ]; then
        echo "[LỖI] Cài đặt không thành công. Vui lòng kiểm tra lại thông báo ở trên."
        exit 1
    fi
fi

# 2. Kích hoạt môi trường ảo
source venv/bin/activate

# 3. Đặt các biến môi trường chuẩn UTF-8
export PYTHONIOENCODING=utf-8
export KMP_DUPLICATE_LIB_OK=TRUE

echo "======================================================================"
echo "  HỆ THỐNG AI OCR CĂN CƯỚC CÔNG DÂN & CMND VIỆT NAM (UBUNTU EDITION)"
echo "======================================================================"
echo "  [INFO] Đang nạp mô hình Deep Learning ngoại tuyến (EasyOCR + CRAFT)..."
echo "  [INFO] Giao diện người dùng Web: http://localhost:8000/demo"
echo "  [INFO] Tài liệu Swagger API:     http://localhost:8000/docs"
echo "  [HƯỚNG DẪN] Nhấn phím Ctrl + C để dừng máy chủ bất cứ lúc nào."
echo "======================================================================"

# 4. Tự động mở trình duyệt web trên Ubuntu Desktop sau khi server sẵn sàng
(
    for i in {1..20}; do
        sleep 0.5
        if command -v curl &>/dev/null && curl -s http://127.0.0.1:8000/api/v1/health &>/dev/null; then
            if command -v xdg-open &>/dev/null; then
                xdg-open "http://localhost:8000/demo" >/dev/null 2>&1 || true
            elif command -v sensible-browser &>/dev/null; then
                sensible-browser "http://localhost:8000/demo" >/dev/null 2>&1 || true
            fi
            break
        fi
    done
) &

# 5. Khởi chạy Backend Server
python3 backend/run_backend.py
