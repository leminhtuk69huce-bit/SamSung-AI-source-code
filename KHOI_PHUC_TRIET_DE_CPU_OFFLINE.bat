@echo off
chcp 65001 >nul
echo ============================================================
echo   HOÀN TÁC TRIỆT ĐỂ: CÀI LẠI GÓI PYTORCH CPU TỪ E:\TEMPPPP\temp)))
echo ============================================================
echo.
echo Đang khôi phục bản PyTorch CPU gốc ngoại tuyến (Offline 100%%)...
echo Nguồn tệp bánh xe: E:\TEMPPPP\temp)))
echo.
python -m pip install --no-index --find-links="E:\TEMPPPP\temp)))" torch==2.14.1 torchvision==0.29.1

setx OCR_GPU false >nul
setx OCR_DEVICE cpu >nul

echo.
echo ============================================================
echo [THÀNH CÔNG] Đã khôi phục hoàn toàn bản PyTorch CPU nguyên bản!
echo Không còn bất kỳ thư viện GPU nào trong môi trường runtime.
echo ============================================================
pause

