#!/usr/bin/env bash
# ==============================================================================
# SCRIPT CHẠY KIỂM THỬ TOÀN DIỆN TRÊN HỆ ĐIỀU HÀNH UBUNTU / LINUX
# DỰ ÁN: AI OCR CĂN CƯỚC CÔNG DÂN & CHỨNG MINH NHÂN DÂN VIỆT NAM
# ==============================================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

if [ ! -d "venv" ]; then
    echo "[INFO] Chưa tìm thấy venv. Đang tự động chạy setup..."
    ./setup_ubuntu.sh
fi

source venv/bin/activate
export PYTHONIOENCODING=utf-8
export KMP_DUPLICATE_LIB_OK=TRUE

echo "======================================================================"
echo "  BẮT ĐẦU CHẠY 10 TEST CASES KIỂM THỬ TRÊN UBUNTU..."
echo "======================================================================"

python3 tests/test_api.py
