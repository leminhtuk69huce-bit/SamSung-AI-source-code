# HƯỚNG DẪN CÀI ĐẶT VÀ CHẠY AI OCR CCCD/CMND TRÊN UBUNTU / LINUX
## DỰ ÁN: SAMSUNG INNOVATION CAMPUS (SIC) AI CAPSTONE PROJECT
### Phiên bản: Ubuntu / Debian / Linux Desktop & Server (Offline Edition)

---

## 1. GIỚI THIỆU PHIÊN BẢN UBUNTU
Đây là bộ mã nguồn hoàn chỉnh của hệ thống **AI OCR Căn cước công dân (CCCD) và Chứng minh nhân dân (CMND) Việt Nam**, được cấu hình và tối ưu hóa chuyên biệt để hoạt động mượt mà trên hệ điều hành **Ubuntu (20.04, 22.04, 24.04 LTS)** cũng như các bản phân phối Linux tương thích (Debian, Linux Mint, Pop!_OS...).

### Cam kết bảo mật & Tính toàn vẹn:
- **100% logic mã nguồn giữ nguyên**: Đầy đủ tính năng tiền xử lý ảnh (CLAHE + Unsharp Masking), nhận diện văn bản (EasyOCR CRAFT + BiLSTM), bóc tách 12 trường dữ liệu tiếng Việt có dấu, quy tắc suy luận giới tính, từ điển 63 tỉnh/thành phố và tự động xuất JSON khi xác nhận.
- **Bảo mật tuyệt đối**: Toàn bộ dữ liệu mẫu, lịch sử quét và ảnh cá nhân từ máy gốc đã được loại bỏ hoàn toàn. Khi bạn khởi chạy trên máy của mình, hệ thống sẽ tự động khởi tạo cơ sở dữ liệu SQLite mới hoàn toàn sạch sẽ và an toàn.
- **Mô hình AI ngoại tuyến (Offline Ready)**: Thư mục `backend/models/` đã tích hợp sẵn trọng số mô hình `craft_mlt_25k.pth` (~83MB) và `latin_g2.pth` (~15MB), bạn có thể chạy ngay lập tức mà không cần mạng Internet để tải thêm trọng số.

---

## 2. CẤU TRÚC THƯ MỤC DỰ ÁN

```
Ubuntu/
├── backend/
│   ├── app/
│   │   ├── api/             # API Endpoints (OCR, Lịch sử, Thống kê)
│   │   ├── services/        # Nghiệp vụ AI OCR, Card Detector, Extractor, Preprocessor
│   │   ├── config.py        # Cấu hình đường dẫn động tương thích Linux
│   │   ├── database.py      # Quản trị CSDL SQLite (tự động khởi tạo bảng)
│   │   ├── main.py          # Khởi tạo ứng dụng FastAPI và Uvicorn
│   │   └── schemas.py       # Pydantic Schemas dữ liệu chuẩn
│   ├── models/              # Trọng số AI EasyOCR offline (CRAFT + Latin)
│   ├── storage/             # Thư mục lưu ảnh quét cục bộ (sạch sẽ, chỉ có .gitkeep)
│   ├── requirements.txt     # Danh sách thư viện Python cần thiết
│   └── run_backend.py       # Script khởi động máy chủ Backend
├── demo_ui/
│   └── index.html           # Giao diện người dùng Web Vanilla cao cấp (Single Page)
├── tests/
│   └── test_api.py          # Bộ kiểm thử 10 Test Cases tự động
├── setup_ubuntu.sh          # Script tự động cài đặt môi trường chỉ với 1 lệnh
├── run.sh                   # Script khởi chạy ứng dụng 1-click
├── test.sh                  # Script chạy toàn bộ test cases kiểm thử
├── Dockerfile               # Tệp cấu hình Docker container
├── docker-compose.yml       # Cấu hình chạy nhanh bằng Docker Compose
├── .gitignore               # Tự động loại trừ cache, CSDL và file tạm
└── README_UBUNTU.md         # Tài liệu hướng dẫn này
```

---

## 3. HƯỚNG DẪN KHỞI CHẠY NHANH

### Cách 1: Khởi chạy tự động 1-Click (Khuyên dùng)
Mở Terminal tại thư mục `Ubuntu/` và chạy 2 lệnh sau:

```bash
# 1. Cấp quyền thực thi cho các script (chỉ cần làm 1 lần đầu)
chmod +x setup_ubuntu.sh run.sh test.sh

# 2. Khởi chạy ứng dụng (nếu chưa có môi trường ảo, script sẽ tự động cài đặt)
./run.sh
```

- Hệ thống sẽ tự động kích hoạt môi trường ảo `venv`, khởi động máy chủ FastAPI tại cổng `8000` và tự động mở trình duyệt web đến địa chỉ:
  👉 **http://localhost:8000/demo**
- Nhấn `Ctrl + C` trên terminal để tắt máy chủ khi dùng xong.

---

### Cách 2: Cài đặt và chạy thủ công từng bước

Nếu bạn muốn kiểm soát từng bước cài đặt trên Ubuntu:

#### Bước 1: Cài đặt các gói hệ thống cần thiết (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv libgl1 libglib2.0-0 curl
```

#### Bước 2: Tạo môi trường ảo Python
```bash
# Tạo thư mục venv
python3 -m venv venv

# Kích hoạt môi trường ảo
source venv/bin/activate
```

#### Bước 3: Cài đặt các thư viện Python
```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

#### Bước 4: Khởi chạy máy chủ
```bash
python3 backend/run_backend.py
```
Mở trình duyệt web của bạn và truy cập: **http://localhost:8000/demo**

---

### Cách 3: Chạy bằng Docker (Không cần cài Python trên máy)

Nếu máy bạn đã cài sẵn **Docker** và **Docker Compose**:

```bash
# 1. Build và khởi chạy container
docker compose up -d

# 2. Xem log hoạt động
docker compose logs -f

# 3. Mở trình duyệt tại: http://localhost:8000/demo
# Để dừng container khi dùng xong:
docker compose down
```

---

## 4. CHẠY KIỂM THỬ TOÀN DIỆN (10/10 TEST CASES)

Hệ thống đi kèm bộ kiểm thử tự động toàn diện kiểm tra tất cả các API (Root, Health Check, Stats, Upload Scan, Webcam Scan, Lịch sử, Cập nhật thông tin, Xuất file Excel/CSV, Xóa bản ghi).

Chỉ cần chạy lệnh:
```bash
./test.sh
```
Hoặc:
```bash
source venv/bin/activate
python3 tests/test_api.py
```

Kết quả mong đợi:
```
============================================================
BẮT ĐẦU CHẠY KIỂM THỬ TOÀN DIỆN BACKEND OCR API...
============================================================
[TEST 1] Kiểm tra endpoint gốc '/'... -> PASSED
[TEST 2] Kiểm tra endpoint '/api/v1/health'... -> PASSED
[TEST 3] Kiểm tra endpoint '/api/v1/ocr/stats'... -> PASSED
[TEST 4] Kiểm tra OCR trích xuất từ file tải lên '/api/v1/ocr/scan'... -> PASSED
[TEST 5] Kiểm tra lấy danh sách lịch sử '/api/v1/ocr/history'... -> PASSED
[TEST 6] Kiểm tra lấy chi tiết bản ghi... -> PASSED
[TEST 7] Kiểm tra cập nhật thông tin... -> PASSED
[TEST 8] Kiểm tra xuất file Excel & CSV... -> PASSED
[TEST 9] Kiểm tra API Webcam scan (Base64)... -> PASSED
[TEST 10] Kiểm tra xóa bản ghi... -> PASSED
============================================================
🎉 TẤT CẢ 10/10 TEST CASES ĐÃ PASS 100% THÀNH CÔNG!
============================================================
```

---

## 5. HƯỚNG DẪN SỬ DỤNG TÍNH NĂNG TRÊN GIAO DIỆN WEB

1. **Quét ảnh thẻ**:
   - **Tải ảnh có sẵn**: Chọn tab "Tải ảnh tệp tin", kéo thả hoặc chọn ảnh thẻ từ máy tính.
   - **Chụp từ Webcam trực tiếp**: Chọn tab "Chụp ảnh Webcam" $\rightarrow$ cho phép trình duyệt truy cập Camera $\rightarrow$ bấm "Chụp ảnh" (khung hình sẽ đóng băng để kiểm tra độ rõ) $\rightarrow$ bấm "Trích xuất thông tin".
   - **Quét cả 2 mặt**: Chọn tab "Quét 2 mặt (Dual-Side)" để lần lượt chụp Mặt trước và Mặt sau, hệ thống sẽ tự động ghép thành 1 hồ sơ duy nhất.
2. **Kiểm tra và Sửa dữ liệu (Human-in-the-Loop)**:
   - Các trường thông tin (Số CCCD, Họ tên, Ngày sinh, Quê quán, Nơi thường trú...) được điền vào từng ô input tương ứng.
   - Khi di chuột vào ô nhập liệu, hộp bao tương ứng trên ảnh sẽ tự động sáng viền để bạn đối soát.
   - Nếu ảnh gốc mờ, bạn có thể click sửa trực tiếp trên từng ô.
3. **Xác nhận và Xuất file JSON tự động**:
   - Sau khi kiểm tra thông tin, bấm nút xanh **"Xác nhận & Lưu vào hệ thống"**.
   - Bản ghi sẽ được đánh dấu đã duyệt trong CSDL, đồng thời **trình duyệt sẽ tự động tải file JSON kết quả về máy tính của bạn**.
4. **Tra cứu lịch sử & Xuất báo cáo**:
   - Chuyển sang tab "Lịch sử & Thống kê" để tìm kiếm, xem lại hồ sơ cũ, xem biểu đồ tỷ lệ thẻ và bấm nút xuất báo cáo ra file **Excel (.xlsx)** hoặc **CSV**.

---

## 6. XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)

1. **Lỗi: `Permission denied: ./run.sh`**:
   - Khắc phục: Chạy `chmod +x *.sh` để cấp quyền thực thi.
2. **Lỗi: `libGL.so.1: cannot open shared object file`**:
   - Khắc phục: Thiếu thư viện đồ họa hệ thống cho OpenCV, chạy lệnh:
     ```bash
     sudo apt install -y libgl1 libglib2.0-0
     ```
3. **Lỗi: Trình duyệt không mở được Webcam**:
   - Trình duyệt Chrome/Firefox trên Linux yêu cầu bạn bấm "Cho phép (Allow)" quyền truy cập Camera khi có thông báo hỏi.
   - Nếu dùng kết nối từ xa hoặc IP khác ngoài `localhost`, trình duyệt sẽ chặn webcam do chưa có HTTPS. Hãy truy cập đúng địa chỉ `http://localhost:8000/demo` hoặc `http://127.0.0.1:8000/demo`.
4. **Cổng 8000 đã bị ứng dụng khác chiếm**:
   - Hệ thống có cơ chế tự động tìm cổng rảnh kế tiếp (8001, 8002, 8080...). Hãy xem địa chỉ cổng thực tế được in trên Terminal khi khởi động.
