@echo off
chcp 65001 >nul
echo ============================================================
echo   CHUYỂN HỆ THỐNG OCR SANG CHẾ ĐỘ: CPU (AN TOÀN & ỔN ĐỊNH)
echo ============================================================
echo.
echo Đang cấu hình chế độ chạy trên CPU (Đường lui an toàn)...
set OCR_GPU=false
set OCR_DEVICE=cpu
setx OCR_GPU false >nul
setx OCR_DEVICE cpu >nul

echo [OK] Đã thiết lập OCR_GPU=false và OCR_DEVICE=cpu!
echo [OK] Hệ thống sẽ chạy hoàn toàn trên CPU mà không cần GPU.
echo.
echo Nhấn phím bất kỳ để đóng...
pause >nul

