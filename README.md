# 🪪 HỆ THỐNG NHẬN DIỆN VÀ TRÍCH XUẤT THÔNG TIN CCCD/CMND BẰNG HỌC MÁY TRÊN NỀN TẢNG LOCALHOST PHỤC VỤ ĐA NGƯỜI DÙNG

## ĐỀ TÀI CAPSTONE PROJECT - SAMSUNG INNOVATION CAMPUS (SIC)
Dự án ứng dụng Deep Learning / OCR tiên tiến (CRAFT Text Detection + EasyOCR + Vietnamese Post-Processor) để nhận diện và bóc tách tự động thông tin từ Căn cước công dân (CCCD có chip, mã vạch) và Chứng minh nhân dân (CMND 9 số, 12 số) qua **Webcam máy tính trực tiếp** hoặc **File ảnh tải lên**.

---

## 📁 CẤU TRÚC THƯ MỤC DỰ ÁN

```
e:\Samsung source code\
├── OCR_CCCD.exe                   # File chạy duy nhất (1-Click Native Launcher)
├── backend/                       # Source code Backend FastAPI
│   ├── app/
│   │   ├── api/                   # API Endpoints (OCR, History, Stats)
│   │   ├── services/              # ML OCR Engine, Preprocessor, Extractor
│   │   ├── config.py              # Cấu hình hệ thống
│   │   ├── database.py            # SQLite database & queries
│   │   ├── schemas.py             # Pydantic schemas
│   │   └── main.py                # FastAPI app & routing
│   ├── storage/                   # Thư mục lưu trữ ảnh thẻ đã xử lý
│   ├── requirements.txt           # Danh sách thư viện Python
│   └── run_backend.py             # File chạy server backend từ source
│
├── demo_ui/                       # Giao diện Web PC quét Webcam trực tiếp
│   └── index.html                 # Giao diện Vanilla hiện đại, không cần Node.js
│
├── tests/                         # Bộ kiểm thử tự động
│   └── test_api.py                # Bộ test cases API tự động
│
├── docs/                          # Tài liệu kỹ thuật & Đặc tả giao diện
│   ├── YEU_CAU_GIAO_DIEN_UI_UX.md # Đặc tả chi tiết UI/UX cho AI / Dev Frontend
│   └── PROMPT_CHO_AI_FRONTEND.md  # Prompt copy-paste sẵn để đưa cho AI khác làm UI
│
├── Dữ liệu mẫu/                   # 48 bộ dữ liệu quét CCCD thực nghiệm
│
├── SIC_AI_Capstone Project_Final Report.docx               # Quyển báo cáo in (Template)
├── SIC_AI_Capstone Project_Presentation Slide Template.pptx # Slides báo cáo (Template)
└── SIC_AI_Capstone Project_Action Plan.docx                # Kế hoạch hành động (Template)
```

---

## ⚡ HƯỚNG DẪN KHỞI CHẠY HỆ THỐNG

### Cách 1: Khởi chạy 1-Click bằng file EXE duy nhất (Khuyên dùng)
Chỉ cần nhấp đúp chuột vào file:
```
OCR_CCCD.exe
```
(tại thư mục gốc của dự án). Hệ thống sẽ tự động khởi động server và mở trình duyệt web.

### Cách 2: Chạy từ mã nguồn Python (Dành cho Lập trình viên)
```powershell
cd "e:\Samsung source code\backend"
$env:KMP_DUPLICATE_LIB_OK="TRUE"
"C:\Users\Acer\anaconda3\python.exe" run_backend.py
```

Sau khi chạy, hệ thống sẽ mở các cổng dịch vụ tại:
- **Giao diện Web PC (Live Webcam Scanner):** [http://localhost:8000/demo](http://localhost:8000/demo) (hoặc [http://localhost:8000](http://localhost:8000))
- **Tài liệu API tương tác (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Tài liệu API Redoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 CHẠY KIỂM THỬ TỰ ĐỘNG (AUTOMATED TESTS)

Hệ thống đã tích hợp sẵn test suite kiểm thử toàn diện mọi API và trích xuất dữ liệu mẫu:
```powershell
cd "e:\Samsung source code"
$env:KMP_DUPLICATE_LIB_OK="TRUE"
"C:\Users\Acer\anaconda3\python.exe" tests/test_api.py
```
**Kết quả kiểm thử:** `10/10 TEST CASES PASS 100%`.

---

## 📑 BÀN GIAO CHO AI LÀM GIAO DIỆN FRONTEND

Nếu bạn muốn một AI khác (Claude, ChatGPT, v.v.) viết giao diện React / Vite / Tailwind đẹp hơn nữa:
1. Mở file [docs/PROMPT_CHO_AI_FRONTEND.md](file:///e:/Samsung%20source%20code/docs/PROMPT_CHO_AI_FRONTEND.md).
2. **Copy toàn bộ nội dung prompt** và gửi cho AI đó.
3. Tài liệu chi tiết mọi endpoint, JSON mẫu và Type định nghĩa tại [docs/YEU_CAU_GIAO_DIEN_UI_UX.md](file:///e:/Samsung%20source%20code/docs/YEU_CAU_GIAO_DIEN_UI_UX.md).
