# QUY CHUẨN DỰ ÁN: AI OCR CCCD / CMND VIỆT NAM (ocr-vietnam-optimizer)

Mọi AI Assistant và Lập trình viên khi làm việc trên kho mã nguồn này BẮT BUỘC tuân thủ các quy tắc cốt lõi (3 trong 1) sau:

---

## 1. TĂNG TỐI ĐA HIỆU SUẤT (PERFORMANCE)
- **Singleton Pattern cho OCR Reader**:
  Chỉ khởi tạo mô hình EasyOCR duy nhất một lần khi server khởi động (lưu trữ trong `ocr_engine.py` / `lifespan`). Tuyệt đối không re-init hoặc tải lại mô hình trên mỗi request.
- **Tối ưu kích thước ảnh đầu vào**:
  Tự động co giãn (resize) ảnh về ngưỡng chuẩn dài nhất từ **1280px đến 1600px** trước khi đưa vào Deep Learning inference để giảm tải CPU 4-8 lần mà vẫn đảm bảo độ sắc nét nhận diện.
- **Bất đồng bộ tác vụ CPU-bound**:
  Đưa tiến trình chạy OCR vào `run_in_threadpool` (hoặc background worker thread) để giữ Event Loop của FastAPI luôn thông suốt, giao diện phản hồi mượt mà.

---

## 2. TUYỆT ĐỐI ĐỘ CHÍNH XÁC (ACCURACY & ZERO TEXT LEAKS)
- **Multi-date Heuristic (Phân định ngày tháng)**:
  - Tách biệt rõ ràng **Ngày sinh** (`năm <= 2024`, gắn liền ngữ cảnh `sinh` / `birth`) và **Ngày hết hạn** (`năm >= 2025` hoặc chuỗi `"Không thời hạn"`, gắn liền ngữ cảnh `giá trị đến` / `cógiá` / `expiry` / `hết hạn`).
  - Không được để trống một trong hai trường nếu ảnh có chứa ngày tháng hợp lệ.
- **Clean Address (Làm sạch chuỗi địa chỉ)**:
  - Dùng regex loại bỏ triệt để các nhãn rác in đè/chảy chữ từ dòng hạn dùng: `'có giá trị đến'`, `'cógiá tíđến'`, `'tíđến'`, `'date of expiry'`, `'ofexpiry'`.
  - Tự động gộp âm tiết tiếng Việt bị chia tách nhầm bởi dấu phẩy (ví dụ: `'Đại, áng'` ➔ `'Đại Áng'`).
  - Chuẩn hóa khoảng trắng và dấu phẩy ngăn cách xã/huyện/tỉnh.
- **Suy luận thông minh từ 12 số CCCD**:
  - Chữ số thứ 4: **0, 2, 4, 6, 8** ➔ **Nam**; **1, 3, 5, 7, 9** ➔ **Nữ** (độ tin cậy 95% khi OCR đọc chữ Nam/Nữ bị mờ hoặc lóa).

---

## 3. ĐƠN GIẢN HÓA CODE NHƯNG ĐẦY ĐỦ 100% TÍNH NĂNG (CLEAN ARCHITECTURE)
- **Cấu trúc Clean Code & Tối Giản**:
  - Tách lớp rõ ràng:
    - `backend/app/services/`: Nghiệp vụ cốt lõi (`ocr_engine.py`, `preprocessor.py`, `extractor.py`, `export_service.py`).
    - `backend/app/api/`: Định nghĩa API endpoints (`ocr_routes.py`, `history_routes.py`, `stats_routes.py`).
    - `backend/app/database.py`: Quản trị CSDL SQLite gọn nhẹ với `sqlite3` chuẩn (không cần ORM cồng kềnh).
    - `demo_ui/`: Giao diện web Vanilla (HTML/CSS/JS) chuẩn cao cấp, không dùng node_modules phức tạp.
- **Quy trình chụp Webcam 2 giai đoạn (Capture & Review)**:
  - *Giai đoạn 1 (Chụp)*: Video live camera ➔ Bấm "Chụp ảnh" (`#btn-capture-photo`) ➔ Đóng băng hiển thị frame trên `<img>` ➔ Tạm ẩn video stream.
  - *Giai đoạn 2 (Duyệt)*: Hiện cụm nút `[Chụp lại]` (trở lại xem live) và `[Trích xuất thông tin]` (gửi ảnh đã đóng băng lên API `/api/v1/ocr/scan-webcam`).
- **Giao diện bảng kết quả tương tác (Inline Editable & Confirmation)**:
  - Tất cả các trường thông tin hiển thị trên từng ô input tương ứng, cho phép người dùng click sửa trực tiếp nếu ảnh gốc bị mờ.
  - Nút **"Xác nhận & Lưu vào hệ thống"** lưu dữ liệu hoàn chỉnh vào SQLite và hiển thị Modal popup thông báo xác nhận thành công.
  - Hỗ trợ xuất dữ liệu ra file **Excel (.xlsx)**, **CSV**, và **JSON**.
