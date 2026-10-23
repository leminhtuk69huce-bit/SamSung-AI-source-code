# Hướng Dẫn Sử Dụng Bản Chạy Độc Lập (EXE) — OCR CCCD & CMND

## 📌 Tổng Quan
Dự án đã được hoàn thiện và cấu hình tối ưu thành **DUY NHẤT 1 FILE THỰC THI** tại thư mục gốc:
```
e:\Samsung source code\OCR_CCCD.exe
```
- **Không cần cài đặt Python** hay môi trường dòng lệnh phức tạp.
- **Không có các file .bat rườm rà**: Toàn bộ hệ thống chạy qua duy nhất 1 file `OCR_CCCD.exe`.
- Tích hợp sẵn toàn bộ mô hình AI OCR (EasyOCR CRAFT + Latin Recognition ngoại tuyến), FastAPI backend, và giao diện web hiện đại.
- **Tự động mở trình duyệt web** đến giao diện người dùng ngay khi AI sẵn sàng.
- **Cơ chế chống tắt đột ngột (No-Crash & Resilient Port)**: Tự động phát hiện và chuyển cổng thông minh nếu cổng 8000 bị xung đột, giữ cửa sổ console luôn mở để người dùng kiểm soát.

---

## 🚀 Cách Khởi Chạy

Bạn chỉ cần **click đúp chuột** vào file:
```
OCR_CCCD.exe
```
Ứng dụng sẽ tự động:
1. **Dọn dẹp & kiểm tra tài nguyên**: Giải phóng các tiến trình cũ nếu có.
2. **Khởi động AI OCR Server**: Nạp mô hình Deep Learning vào bộ nhớ (Singleton Pattern).
3. **Mở trình duyệt web**: Tự động mở trang giao diện `http://127.0.0.1:8000/demo/` (hoặc cổng 8001/8080 nếu 8000 bị chiếm).

---

## 🛑 Cách Dừng Hệ Thống
- Khi muốn tắt ứng dụng, chỉ cần nhấn tổ hợp phím **Ctrl + C** trên cửa sổ console hoặc đóng cửa sổ `OCR_CCCD.exe`.
- Hệ thống sẽ tự động dọn dẹp tiến trình nền an toàn.

