# 🪪 HỆ THỐNG AI OCR NHẬN DIỆN VÀ TRÍCH XUẤT THÔNG TIN CCCD/CMND VIỆT NAM

## 🌟 ĐỀ TÀI CAPSTONE PROJECT — SAMSUNG INNOVATION CAMPUS (SIC)
Dự án ứng dụng mô hình Học sâu (Deep Learning) và Nhận diện ký tự quang học (OCR) tiên tiến kết hợp hệ chuyên gia Heuristics tiếng Việt để tự động phát hiện, cắt viền, đọc và trích xuất có cấu trúc thông tin từ Căn cước công dân (CCCD có chip, mã vạch) và Chứng minh nhân dân (CMND 9 số, 12 số).

Hệ thống vận hành **hoàn toàn ngoại tuyến (Offline / On-Premise)** trên máy tính cục bộ, bảo vệ tối đa dữ liệu riêng tư của công dân, hỗ trợ cả hai hệ điều hành **Windows** và **Ubuntu / Linux**.

---

## ✨ CÁC TÍNH NĂNG NỔI BẬT

1. **Hỗ trợ đa dạng phương thức nạp ảnh**:
   - **Chụp Webcam trực tiếp 2 giai đoạn (Capture & Review)**: Khung ngắm chuẩn tỷ lệ thẻ ISO/IEC 7810 ID-1, đóng băng khung hình để người dùng kiểm tra độ nét trước khi quét.
   - **Tải ảnh tệp tin**: Hỗ trợ định dạng JPG, PNG, JPEG từ máy tính hoặc điện thoại.
   - **Quét kết hợp 2 mặt (Dual-Side Scan)**: Lần lượt quét Mặt trước và Mặt sau để tổng hợp thành một hồ sơ duy nhất.
2. **Tiền xử lý ảnh thông minh**:
   - Tự động phát hiện 4 góc thẻ và nắn thẳng phối cảnh (Perspective Transform).
   - Tăng cường độ tương phản thích nghi (CLAHE) kết hợp bộ lọc Unsharp Masking làm sắc nét các dấu thanh tiếng Việt bị mờ nhạt.
   - Co giãn kích thước ảnh thích nghi về cạnh dài chuẩn 1280px để tối ưu tốc độ xử lý.
3. **Mô hình OCR kép và Bộ bóc tách Heuristics chuyên sâu**:
   - Phát hiện vùng văn bản bằng mạng CRAFT và nhận dạng chuỗi bằng mạng CRNN (BiLSTM + CTC).
   - **Multi-date Heuristic**: Phân định chính xác Ngày sinh ($\le 2024$) và Hạn dùng ($\ge 2025$ hoặc "Không thời hạn").
   - **Chuẩn hóa số định danh**: Tự động sửa các lỗi OCR nhầm giữa chữ cái và số ($O \rightarrow 0, I \rightarrow 1, B \rightarrow 8, S \rightarrow 5$).
   - **Suy luận giới tính**: Phân tích chữ số thứ 4 của mã định danh 12 số (chẵn là Nam, lẻ là Nữ) đạt độ tin cậy 95%.
   - **Chuẩn hóa địa chỉ**: Khớp từ điển 63 Tỉnh/Thành phố Việt Nam, tự động sửa dấu và gộp âm tiết bị ngắt nhầm.
   - **Tự sinh mã MRZ**: Tái tạo chuỗi 3 dòng chuẩn ICAO Doc 9303 TD1 mặt sau.
4. **Kiểm duyệt trực quan (Human-in-the-Loop) & Xuất dữ liệu**:
   - Bố cục 2 cột song song (Side-by-side): Khung ảnh có hộp bao chữ nhật (Bounding Boxes) đổi màu phát sáng đồng bộ khi rê chuột vào ô nhập liệu.
   - Cho phép người dùng click sửa trực tiếp (Inline Editing) nếu ảnh gốc bị mờ xước.
   - **Tự động tải file JSON kết quả** ngay khi bấm nút "Xác nhận & Lưu vào hệ thống".
   - Quản lý lịch sử quét, tìm kiếm tức thời, xem lại ảnh gốc và xuất báo cáo ra **Excel (.xlsx)** hoặc **CSV (UTF-8 BOM)**.

---

## 📁 CẤU TRÚC THƯ MỤC DỰ ÁN

```
.
├── OCR_CCCD.exe              # [Windows] Bản chạy 1-click duy nhất (Native Portable Launcher)
├── backend/                  # Mã nguồn Backend máy chủ FastAPI
│   ├── app/
│   │   ├── api/              # API Endpoints (OCR, Lịch sử, Thống kê)
│   │   ├── services/         # Mô hình OCR Engine, Card Detector, Preprocessor, Extractor
│   │   ├── config.py         # Cấu hình hệ thống động
│   │   ├── database.py       # Quản trị CSDL SQLite (tự động khởi tạo bảng)
│   │   ├── schemas.py        # Pydantic Schemas kiểm duyệt dữ liệu
│   │   └── main.py           # FastAPI application & lifespan
│   ├── models/               # Trọng số AI offline (craft_mlt_25k.pth & latin_g2.pth)
│   ├── storage/              # Thư mục lưu ảnh cục bộ an toàn
│   ├── requirements.txt      # Danh sách thư viện Python
│   └── run_backend.py        # File khởi chạy server từ mã nguồn
│
├── demo_ui/                  # Giao diện Web PC quét Webcam & Upload
│   └── index.html            # Giao diện Vanilla HTML5/CSS3/JS cao cấp (Single Page)
│
├── Ubuntu/                   # [Ubuntu / Linux] Phiên bản độc lập dành cho Linux
│   ├── setup_ubuntu.sh       # Script tự động cài môi trường, venv và dependencies
│   ├── run.sh                # Script khởi chạy 1-click trên Ubuntu
│   ├── test.sh               # Script chạy kiểm thử tự động trên Ubuntu
│   ├── Dockerfile            # Cấu hình container Docker
│   ├── docker-compose.yml    # Khởi chạy nhanh bằng Docker Compose
│   └── README_UBUNTU.md      # Tài liệu hướng dẫn riêng cho người dùng Ubuntu
│
├── tests/                    # Bộ kiểm thử tự động toàn diện
│   └── test_api.py           # 10 Test Cases kiểm tra toàn bộ API (PASSED 100%)
│
└── docs/                     # Tài liệu thiết kế kỹ thuật & phân tích hệ thống
    ├── BAO_CAO_CHI_TIET_FORM_USE_CASE.md # Đặc tả 5 Use Cases cốt lõi chuẩn RUP
    ├── DE_CUONG_VA_NOI_DUNG_CHUONG_2.md  # Nội dung chi tiết Chương 2 thiết kế hệ thống
    └── DAN_Y_BAO_CAO_CHUAN_HOA.md        # Khung dàn ý báo cáo 4 chương chuẩn 30-40 trang
```

---

## ⚡ HƯỚNG DẪN KHỞI CHẠY HỆ THỐNG

### 1. Trên hệ điều hành Windows

#### Cách 1: Khởi chạy 1-Click bằng file EXE (Khuyên dùng nhất)
Nhấp đúp chuột vào file:
```
OCR_CCCD.exe
```
Hệ thống sẽ tự động giải phóng tiến trình cũ, nạp mô hình AI ngoại tuyến vào bộ nhớ (Singleton Pattern), tự động chọn cổng mạng rảnh (8000, 8001, 8080) và mở trình duyệt web lên.

#### Cách 2: Khởi chạy từ mã nguồn Python
```bash
# Di chuyển vào thư mục backend
cd backend

# Cài đặt thư viện phụ thuộc (nếu chưa cài)
pip install -r requirements.txt

# Khởi chạy server
python run_backend.py
```

---

### 2. Trên hệ điều hành Ubuntu / Linux

Mở Terminal tại thư mục `Ubuntu/` và chạy:
```bash
# Cấp quyền thực thi và khởi chạy 1-click
chmod +x setup_ubuntu.sh run.sh test.sh
./run.sh
```
*(Hệ thống sẽ tự động tạo môi trường ảo `venv`, cài các gói thư viện và mở trình duyệt web tại `http://localhost:8000/demo`)*.

Hoặc khởi chạy bằng **Docker**:
```bash
cd Ubuntu
docker compose up -d
```

---

## 🌐 ĐỊA CHỈ TRUY CẬP DỊCH VỤ

Khi máy chủ khởi động thành công:
- **Giao diện Web Người dùng:** [http://localhost:8000/demo](http://localhost:8000/demo) (hoặc [http://127.0.0.1:8000/demo](http://127.0.0.1:8000/demo))
- **Tài liệu API tương tác (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Tài liệu API Redoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 CHẠY KIỂM THỬ TỰ ĐỘNG (AUTOMATED TESTS)

Hệ thống tích hợp sẵn bộ kiểm thử tự động 10 kịch bản bao phủ từ khởi động, health check, upload file, webcam base64, cập nhật thông tin, xuất file Excel/CSV đến xóa bản ghi:
```bash
python tests/test_api.py
```
**Kết quả kiểm thử:** `🎉 TẤT CẢ 10/10 TEST CASES ĐÃ PASS 100% THÀNH CÔNG!`

---

## 🔒 CHÍNH SÁCH BẢO MẬT & QUYỀN RIÊNG TƯ

- **100% On-Premise**: Toàn bộ tiến trình xử lý hình ảnh và lưu trữ cơ sở dữ liệu diễn ra hoàn toàn trên thiết bị nội bộ của bạn.
- **Không rò rỉ dữ liệu cá nhân**: Các tệp ảnh quét thực nghiệm, cơ sở dữ liệu và file tạm được cấu hình tự động loại trừ khỏi Git thông qua `.gitignore`.
- **Tuân thủ pháp luật**: Thiết kế tuân thủ quy chuẩn về bảo vệ dữ liệu cá nhân theo Nghị định số 13/2023/NĐ-CP của Chính phủ.
