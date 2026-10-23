---
name: ocr-vietnam-optimizer
description: >-
  Bộ kỹ năng và quy chuẩn tối ưu hóa toàn diện cho hệ thống AI OCR CCCD/CMND Việt Nam:
  tăng hiệu suất xử lý (CPU/GPU, bộ nhớ, phản hồi nhanh), nâng cao độ chính xác bóc tách
  (chính xác ngày sinh/hết hạn, làm sạch địa chỉ, suy luận giới tính/quê quán qua 12 số CCCD),
  và đơn giản hóa mã nguồn (kiến trúc tối giản, dễ bảo trì) nhưng đầy đủ 100% tính năng.
  Kích hoạt khi xây dựng, tinh chỉnh hoặc gỡ lỗi các hệ thống OCR giấy tờ tùy thân Việt Nam.
---

# 🚀 Bộ Kỹ Năng: Tối Ưu Hóa AI OCR CCCD / CMND Việt Nam

Tài liệu hướng dẫn quy chuẩn toàn diện giúp AI và Lập trình viên xây dựng hệ thống OCR thẻ căn cước đạt 3 mục tiêu cốt lõi:
1. **Tối Đa Hiệu Suất (Performance & Speed)**
2. **Tuyệt Đối Độ Chính Xác (High Precision & Accuracy)**
3. **Mã Nguồn Tối Giản Nhưng Đầy Đủ Tính Năng (Clean, Minimal & 100% Feature-Complete)**

---

## 1. NGUYÊN TẮC TĂNG HIỆU SUẤT (PERFORMANCE OPTIMIZATION)

### 1.1. Khởi Tạo Model Duy Nhất (Singleton Pattern)
- **Tuyệt đối không** khởi tạo lại đối tượng `easyocr.Reader` hoặc tải lại trọng số mô hình PyTorch trong mỗi request.
- Áp dụng Singleton lưu trữ trong module `ocr_engine.py` hoặc nạp sẵn trong `lifespan` của FastAPI khi server khởi động:
  ```python
  _ocr_reader_instance = None

  def get_ocr_engine():
      global _ocr_reader_instance
      if _ocr_reader_instance is None:
          # Nạp 1 lần duy nhất từ thư mục offline cục bộ
          _ocr_reader_instance = easyocr.Reader(['vi', 'en'], gpu=False, model_storage_directory=MODEL_DIR)
      return _ocr_reader_instance
  ```

### 1.2. Tối Ưu Tiền Xử Lý Ảnh Trước Khi Đưa Vào AI
- Kích thước ảnh tối ưu cho thẻ CCCD là chiều dài từ **1280px đến 1600px** (tương đương chuẩn HD/FullHD).
- Ảnh kích thước quá lớn (> 3000px từ máy ảnh cao cấp) làm CPU tốn thời gian xử lý gấp 4-8 lần mà không tăng thêm độ chính xác:
  ```python
  h, w = img.shape[:2]
  max_dim = 1600
  if max(h, w) > max_dim:
      scale = max_dim / float(max(h, w))
      img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
  ```

### 1.3. Cơ Chế Bất Đồng Bộ & Bộ Nhớ (Thread Pool / Async)
- Vì quá trình suy luận Deep Learning (EasyOCR / CRAFT / CRNN) là tác vụ chiếm dụng CPU (CPU-bound), cần chạy trong `run_in_threadpool` của FastAPI / Starlette để không làm nghẽn Event Loop:
  ```python
  from starlette.concurrency import run_in_threadpool
  result = await run_in_threadpool(engine.readtext, processed_image)
  ```

---

## 2. NGUYÊN TẮC TĂNG ĐỘ CHÍNH XÁC (HIGH ACCURACY RULES)

### 2.1. Phân Định Ngày Sinh vs. Ngày Hết Hạn (Multi-Date Heuristic)
Trong ảnh CCCD thường xuất hiện 2 hoặc 3 cụm ngày tháng (`dd/mm/yyyy`). Để không bao giờ bị nhầm lẫn:
- **Heuristic ngữ cảnh**: Tìm từ khóa gần kề:
  - Cụm từ `sinh`, `birth`, `ngày sinh` ➔ **Ngày sinh**.
  - Cụm từ `giá trị đến`, `cógiá`, `tíđến`, `expiry`, `hết hạn` ➔ **Ngày hết hạn**.
- **Heuristic năm (Dải năm logic)**:
  - $\text{Năm sinh} \le \text{Năm hiện tại} - 14$ (Ví dụ $\le 2024$).
  - $\text{Năm hết hạn} \ge \text{Năm hiện tại}$ (Ví dụ $\ge 2025$) hoặc giá trị là *"Không thời hạn"*.
  - Nếu thẻ của công dân tròn 60 tuổi: Hạn dùng là *"Không thời hạn"*.

### 2.2. Làm Sạch Chuỗi Địa Chỉ (Zero Text Leaks)
Nhãn dòng "Có giá trị đến / Date of expiry" thường in ngay bên dưới hoặc nằm sát dòng "Nơi thường trú".
Cần áp dụng bộ lọc regex dọn dẹp triệt để:
```python
def clean_vietnamese_address(raw_str: str) -> str:
    t = raw_str
    # 1. Tách lấy ngày hết hạn nếu bị lọt vào địa chỉ
    # 2. Xóa sạch các nhãn rác OCR thường đọc sai:
    t = re.sub(r"(có\s*giá\s*t[r|i|í]\s*đến|cógiá\s*tíđến|cógiá|tíđến|có\s*giá\s*trị|hết\s*hạn|date\s*of\s*expiry|'ofexpiry|ofexpiry|expiry)[:;]?", "", t, flags=re.IGNORECASE)
    # 3. Gộp các âm tiết tiếng Việt bị dấu phẩy chia tách nhầm (ví dụ: 'Đại, áng' -> 'Đại Áng'):
    t = re.sub(r"\b([A-ZÀ-Ỹa-zà-ỹ]+),\s*([a-zà-ỹ]+)\b", lambda m: m.group(1) + " " + m.group(2).capitalize(), t)
    # 4. Chuẩn hóa dấu phẩy và khoảng trắng:
    t = re.sub(r"\s*,\s*", ", ", t)
    t = re.sub(r",(\s*,)+", ",", t)
    return t.strip(" ,.-:")
```

### 2.3. Quy Tắc Suy Luận Hỗ Trợ Từ 12 Số CCCD
Số CCCD 12 số tuân thủ cấu trúc của Bộ Công An:
`[3 số mã tỉnh][1 số thế kỷ & giới tính][2 số năm sinh][6 số ngẫu nhiên]`
- **Giới tính dự phòng**:
  - Chữ số thứ 4 là **0, 2, 4, 6, 8** ➔ **Nam**
  - Chữ số thứ 4 là **1, 3, 5, 7, 9** ➔ **Nữ**
- Khi OCR bị lóa hoặc nhận diện chữ "Nam/Nữ" mờ, lập tức lấy số thứ 4 của CCCD để điền với độ tin cậy 95%.

---

## 3. NGUYÊN TẮC ĐƠN GIẢN HÓA CODE & BẢO ĐẢM TÍNH NĂNG (CLEAN ARCHITECTURE)

### 3.1. Cấu Trúc Module Rõ Ràng (Tối Giản, Không Thừa Thãi)
```text
backend/
├── app/
│   ├── api/             # Chỉ chứa định nghĩa API routes (HTTP Request/Response)
│   ├── services/        # Logic nghiệp vụ cốt lõi:
│   │   ├── ocr_engine.py    # Nạp model & suy luận bounding boxes
│   │   ├── preprocessor.py  # Cắt góc, xoay, cân bằng sáng CLAHE
│   │   ├── extractor.py     # Regex & heuristics bóc tách trường thông tin
│   │   └── export_service.py# Xuất Excel, CSV, JSON
│   ├── database.py      # SQLite CRUD đơn giản bằng standard sqlite3 (không cần ORM nặng)
│   └── main.py          # Khởi chạy FastAPI + Mount Demo UI
├── demo_ui/             # Giao diện Vanilla HTML/CSS/JS (không cần node_modules phức tạp)
```

### 3.2. Cơ Chế Chụp Ảnh 2 Bước Chuẩn UI/UX (Capture & Review Workflow)
Khi dùng Webcam, không được gửi ảnh ngay trong lúc quay vì camera đang rung.
- **Bước 1 (Chụp & Đóng băng)**:
  - Bấm nút "Chụp ảnh" (`#btn-capture-photo`) ➔ Lấy frame hiện tại vẽ lên Canvas ➔ Đóng băng hiển thị trên `<img>` ➔ Tạm ẩn video stream.
  - Ẩn cụm nút Live, hiện cụm nút Review: `[Chụp lại]` và `[Trích xuất thông tin]`.
- **Bước 2 (Xác nhận gửi OCR)**:
  - Nếu ảnh mờ ➔ Bấm `[Chụp lại]` để quay lại xem live.
  - Nếu ảnh rõ nét ➔ Bấm `[Trích xuất thông tin]` để gửi ảnh base64 đến `/api/v1/ocr/scan-webcam`.

### 3.3. Tương Tác Kết Quả & Xác Nhận (Interactive Fields & Confirmation)
- Mọi trường dữ liệu (`Số CCCD`, `Họ tên`, `Ngày sinh`, `Quê quán`, `Thường trú`, `Hạn dùng`) hiển thị trong từng ô `<input>` để người dùng có thể gõ sửa trực tiếp nếu ảnh gốc bị mờ.
- Nút **"Xác nhận & Lưu vào hệ thống"** cập nhật dữ liệu đã sửa vào CSDL SQLite và hiển thị Modal popup thông báo hoàn tất cùng âm thanh/thông báo trực quan.
- Hỗ trợ xuất dữ liệu ra file `.xlsx`, `.csv`, `.json`.

---

## 4. QUY TRÌNH KIỂM THỬ NHANH (QUICK AUDIT CHECKLIST)

Khi áp dụng skill này, luôn thực hiện kiểm thử theo checklist sau:
1. `GET /docs` ➔ API Swagger phản hồi `200 OK`.
2. `GET /demo/` ➔ UI tải mượt mà dưới 100ms, không phụ thuộc internet bên ngoài.
3. Test quét ảnh mẫu chứa ngày sinh và hạn dùng ➔ Cả 2 trường đều có giá trị, không bị để trống, không bị dính chữ hạn vào địa chỉ.
4. Chụp webcam ➔ Khung hình đứng yên, người dùng chủ động bấm "Trích xuất" mới gửi API.
5. Sửa thử một trường thông tin ➔ Bấm "Xác nhận & Lưu" ➔ Kiểm tra tab "Lịch sử" thấy bản ghi lưu chính xác giá trị đã sửa.
