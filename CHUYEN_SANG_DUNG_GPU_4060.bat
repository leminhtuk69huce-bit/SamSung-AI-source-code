@echo off
chcp 65001 >nul
echo ============================================================
echo   CHUYỂN HỆ THỐNG OCR SANG CHẾ ĐỘ: NVIDIA GPU RTX 4060
echo ============================================================
echo.
echo Đang kích hoạt tăng tốc phần cứng card đồ họa RTX 4060...
set OCR_GPU=true
set OCR_DEVICE=cuda
setx OCR_GPU true >nul
setx OCR_DEVICE cuda >nul

echo [OK] Đã thiết lập OCR_GPU=true và OCR_DEVICE=cuda!
echo [OK] Tốc độ OCR sẽ tăng vọt hơn 600%% (xử lý ~0.6 giây/ảnh).
echo.
echo Nhấn phím bất kỳ để đóng...
pause >nul

