# 🎨 TÀI LIỆU ĐẶC TẢ YÊU CẦU GIAO DIỆN (UI/UX SPECIFICATION)
## HỆ THỐNG OCR NHẬN DIỆN VÀ TRÍCH XUẤT THÔNG TIN CCCD/CMND QUA WEBCAM PC & UPLOAD ẢNH

> **Dành cho:** AI / Frontend Developer xây dựng giao diện người dùng.  
> **Backend API URL:** `http://localhost:8000` (FastAPI, đã hoạt động và pass 100% test).  
> **Tài liệu Swagger OpenAPI:** `http://localhost:8000/docs`  
> **Phạm vi nền tảng:** **Chỉ dùng trên PC / Máy tính để bàn / Laptop** (không làm Mobile App).  

---

## 1. TRIẾT LÝ THIẾT KẾ & PHONG CÁCH TỔNG THỂ (DESIGN SYSTEM)

- **Phong cách:** Modern eKYC FinTech Dashboard — phong cách bảo mật cao cấp, tinh tế, hiện đại giống các hệ thống eKYC của ngân hàng lớn (MB Bank, Techcombank, Apple Card).
- **Theme:** Hỗ trợ Dark Mode (mặc định nền Slate-900 / Zinc-950) tạo cảm giác công nghệ cao và bảo vệ mắt khi làm việc ban đêm; có nút chuyển Light Mode nếu cần.
- **Hiệu ứng:** Glassmorphism nhẹ (backdrop-blur), viền border mờ (slate-700/60), animation mượt mà (Framer Motion / Tailwind transitions), laser radar scan line cho webcam.
- **Bảng màu đề xuất (Design Tokens):**
  - **Background:** `#0f172a` (Slate 900) hoặc `#09090b` (Zinc 950)
  - **Card / Surface:** `#1e293b` (Slate 800) với border `#334155` (Slate 700)
  - **Primary Accent:** `#2563eb` - `#3b82f6` (Blue 600 - Blue 500)
  - **Success / Validated:** `#10b981` (Emerald 500)
  - **Warning:** `#f59e0b` (Amber 500)
  - **Danger / Expired:** `#ef4444` (Rose 500)
  - **Highlight Text (Họ tên):** `#fcd34d` (Amber 300) hoặc `#ffffff` (White bold)
- **Typography:** Font chữ không chân hiện đại: `Inter`, `Be Vietnam Pro` hoặc `Plus Jakarta Sans`.

---

## 2. KIẾN TRÚC GIAO DIỆN & CÁC MÀN HÌNH CHÍNH (PAGES & COMPONENTS)

Hệ thống bao gồm thanh điều hướng (Sidebar bên trái hoặc Top Navigation Bar) với 3 khu vực chính:
1. **Trang Quét thẻ (Scanner Station)**: Gồm Quét Webcam PC và Upload ảnh thẻ.
2. **Trang Lịch sử & Quản lý hồ sơ (History Table)**: Bảng dữ liệu đã quét, bộ lọc, tìm kiếm, sửa/xóa, xuất Excel/CSV.
3. **Trang Thống kê Dashboard (Analytics)**: Biểu đồ và chỉ số hiệu năng hệ thống.

---

### MÀN HÌNH 1: QUÉT QUA WEBCAM MÁY TÍNH (LIVE WEBCAM SCANNER - TRỌNG TÂM)

Đây là tính năng quan trọng nhất mà giảng viên yêu cầu! Người dùng đưa thẻ CCCD trước Webcam máy tính và chụp trực tiếp trong trình duyệt.

#### Yêu cầu kỹ thuật & UX:
1. **Khởi tạo Camera PC:**
   - Dùng Web API: `navigator.mediaDevices.getUserMedia({ video: { width: { ideal: 1920, min: 1280 }, height: { ideal: 1080, min: 720 }, facingMode: "user" } })`.
   - Có nút **"Bật Webcam"** / **"Tắt Webcam"** và dropdown chọn thiết bị Camera (nếu máy có nhiều webcam/webcam rời USB).
2. **Khung ngắm căn chỉnh thẻ (Card Overlay Bounding Guide):**
   - Tỷ lệ khung ngắm chuẩn kích thước thẻ CCCD/CMND theo ISO/IEC 7810 ID-1 (tỷ lệ vàng `1.586 : 1`).
   - 4 góc bo của khung ngắm viền màu xanh sáng (`#3b82f6`), độ dày 3px-4px.
   - Vùng xung quanh khung ngắm được làm mờ nhẹ (dark backdrop overlay `rgba(0,0,0,0.6)`).
   - Đường quét Laser xanh (`laser-scan-line`) chạy lên xuống liên tục tạo hiệu ứng radar AI nhận diện quang học.
   - Dòng chữ hướng dẫn động dưới khung: *"Vui lòng đưa thẻ CCCD vào giữa khung ngắm, giữ thẳng và không để bóng lóa"*.
3. **Chế độ chụp & Quét (Snapshot):**
   - Dropdown chọn mặt thẻ: **Tự động** (Auto) | **Mặt trước** (Front) | **Mặt sau** (Back).
   - Nút hành động nổi bật: **"Chụp & Quét OCR"** (Icon tia sét / Camera).
   - Khi bấm Chụp:
     + Chụp một khung hình từ Video stream vẽ ra HTML5 `<canvas>`.
     + Xuất canvas thành Base64 JPEG: `canvas.toDataURL('image/jpeg', 0.95)`.
     + Gửi payload JSON tới API Backend:
       ```json
       POST http://localhost:8000/api/v1/ocr/scan-webcam
       Content-Type: application/json
       {
         "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
         "side_hint": "auto"
       }
       ```
     + Hiệu ứng flash chụp ảnh (white flash 150ms) + âm thanh camera shutter (tùy chọn) + chuyển sang trạng thái Loading Skeleton.

---

### MÀN HÌNH 2: TẢI ẢNH FILE (DRAG & DROP SCANNER)

1. **Vùng kéo thả (Dropzone):**
   - Cho phép kéo thả hoặc click chọn file ảnh (JPG, PNG, JPEG) tối đa 10MB.
   - Cho phép chọn chế độ:
     - **Quét 1 mặt**: Gọi `POST /api/v1/ocr/scan` (multipart/form-data).
     - **Quét cả 2 mặt (Ghép hồ sơ)**: Có 2 ô kéo thả "Mặt trước" và "Mặt sau" -> Gọi `POST /api/v1/ocr/scan-both`.

---

### MÀN HÌNH 3: BẢNG KẾT QUẢ TRÍCH XUẤT (RESULT INSPECTOR & VERIFIER)

Bố cục 2 cột (Side-by-side Layout):

#### Cột Trái: Ảnh thẻ đã quét & Bounding Boxes
- Hiển thị ảnh vừa chụp/upload.
- Vẽ các Bounding Boxes bao quanh các đoạn chữ đã nhận diện (dữ liệu `detected_boxes` từ API).
- Khi rê chuột vào từng trường thông tin bên phải -> Bounding box tương ứng bên ảnh thẻ sáng lên (highlight zoom).

#### Cột Phải: Bảng thông tin chi tiết (Editable Form)
- **Hộp Số CCCD/CMND:** Kích thước font lớn (20px-24px), font mono, viền xanh dạ quang, nút **"Copy"** 1-click có thông báo toast *"Đã sao chép"*.
- **Họ và tên:** Viết in hoa nổi bật màu vàng hổ phách (Amber-300).
- **Các trường thông tin khác (Input Editable):**
  - Ngày sinh (dd/mm/yyyy)
  - Giới tính (Nam / Nữ)
  - Quốc tịch (Việt Nam)
  - Quê quán (địa chỉ nhiều dòng)
  - Nơi thường trú (địa chỉ nhiều dòng)
  - Có giá trị đến (ngày hết hạn hoặc "Không thời hạn")
  - (Mặt sau): Ngày cấp, Nơi cấp (Cục Cảnh sát QLHC về TTXH), Đặc điểm nhận dạng, Mã MRZ.
- **Badge Độ tin cậy (Confidence Score):**
  - Xanh lá (`>= 85%`): Xuất sắc, thông tin rõ nét.
  - Vàng cam (`60% - 84%`): Trung bình, khuyến nghị người dùng kiểm tra lại.
  - Đỏ (`< 60%`): Cảnh báo mờ, nghiêng hoặc lóa sáng.
- **Hộp Cảnh báo thông minh (Warnings):**
  - Tự động hiển thị các cảnh báo từ API (Ví dụ: *"Thẻ đã hết hạn"*, *"Số CCCD không chuẩn 12 số"*...).
- **Nút Hành động:**
  - **"Lưu hồ sơ đã xác thực"**: Gọi `PUT /api/v1/ocr/history/{id}` với dữ liệu đã sửa.
  - **"Xuất file JSON"**: Tải về file `.json` chứa đầy đủ cấu trúc.
  - **"In phiếu thông tin"**: Mở cửa sổ in ấn phiếu thông tin cá nhân A4.

---

### MÀN HÌNH 4: BẢNG LỊCH SỬ QUẢN LÝ (HISTORY MANAGEMENT)

1. **Bộ lọc & Tìm kiếm:**
   - Ô tìm kiếm tức thời (Debounce 300ms) theo Họ tên, Số CCCD, Nơi thường trú (`GET /api/v1/ocr/history?search=...`).
   - Lọc theo loại giấy tờ (Tất cả, CCCD có chip, CMND 12 số, CMND 9 số).
   - Lọc theo mặt thẻ (Mặt trước, Mặt sau, Cả 2 mặt).
2. **Bảng dữ liệu (Data Table):**
   - Các cột: Mã hồ sơ, Thời gian quét, Loại thẻ, Số CCCD, Họ tên, Ngày sinh, Địa chỉ, Độ tin cậy, Trạng thái duyệt, Hành động.
   - Nút hành động trên từng dòng: Xem chi tiết (Modal pop-up), Chỉnh sửa, Xóa (Delete API).
3. **Nút Xuất dữ liệu (Export):**
   - Nút **"Xuất Excel (.xlsx)"** -> Tải file từ `GET /api/v1/ocr/export?format=xlsx`.
   - Nút **"Xuất CSV"** -> Tải file từ `GET /api/v1/ocr/export?format=csv`.

---

### MÀN HÌNH 5: BẢNG ĐIỀU KHIỂN THỐNG KÊ (ANALYTICS DASHBOARD)

1. **4 Thẻ chỉ số tổng quan (KPI Stat Cards):**
   - **Tổng lượt quét**: Số lượng tích lũy (ví dụ: `1,248`).
   - **Lượt quét hôm nay**: Số lượng trong ngày (ví dụ: `35`).
   - **Độ tin cậy trung bình**: Tỷ lệ % (ví dụ: `94.2%`).
   - **Thời gian xử lý trung bình**: Số giây (ví dụ: `1.85s`).
2. **Biểu đồ (Charts - Dùng Recharts / Chart.js):**
   - **Biểu đồ tròn (Donut Chart)**: Tỷ lệ phân bố các loại thẻ (`distribution_by_type`: CCCD_CHIP, CMND_12, CMND_9).
   - **Biểu đồ đường (Line/Area Chart)**: Xu hướng số lượt quét theo ngày trong 7 ngày gần nhất (`recent_daily_trends`).

---

## 3. DANH SÁCH CHI TIẾT CÁC API BACKEND & DỮ LIỆU ĐẦU VÀO / ĐẦU RA

Base URL: `http://localhost:8000`

### 1. Quét từ Webcam PC (Base64)
- **Endpoint:** `POST /api/v1/ocr/scan-webcam`
- **Request Body (JSON):**
  ```json
  {
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "side_hint": "auto"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "id": "31088ff8-c6f4-4176-a3a1-8385e10c832b",
    "created_at": "2026-10-19T21:20:00",
    "document_type": "CCCD_CHIP",
    "side": "FRONT",
    "overall_confidence": 0.944,
    "processing_time_sec": 1.75,
    "fields": {
      "id_number": { "value": "001205051692", "confidence": 1.0 },
      "full_name": { "value": "NGUYỄN LƯƠNG AN", "confidence": 0.72 },
      "date_of_birth": { "value": "27/12/2005", "confidence": 0.75 },
      "gender": { "value": "Nam", "confidence": 1.0 },
      "nationality": { "value": "Việt Nam", "confidence": 0.99 },
      "place_of_origin": { "value": "Sơn Đồng, Hoài Đức, Hà Nội", "confidence": 0.95 },
      "place_of_residence": { "value": "11 Hẻm 66/21 Ngõ Hòa Bình 7, Minh Khai, Hai Bà Trưng, HN", "confidence": 0.90 },
      "date_of_expiry": { "value": "27/12/2030", "confidence": 0.84 },
      "date_of_issue": { "value": null, "confidence": 0.0 },
      "issuing_authority": { "value": null, "confidence": 0.0 },
      "identifying_features": { "value": null, "confidence": 0.0 },
      "mrz_code": { "value": null, "confidence": 0.0 }
    },
    "warnings": [],
    "image_url": "/storage/webcam_31088ff8.jpg",
    "detected_boxes": [
      {
        "box": [[100, 150], [400, 150], [400, 190], [100, 190]],
        "text": "001205051692",
        "confidence": 1.0
      }
    ]
  }
  ```

### 2. Quét từ File Upload (1 ảnh)
- **Endpoint:** `POST /api/v1/ocr/scan`
- **Content-Type:** `multipart/form-data`
- **Form Data:**
  - `file`: `<Binary Image>`
  - `side_hint`: `"auto"` (hoặc `"front"`, `"back"`)
- **Response:** Cấu trúc tương tự API Webcam.

### 3. Quét đồng thời 2 mặt thẻ
- **Endpoint:** `POST /api/v1/ocr/scan-both`
- **Content-Type:** `multipart/form-data`
- **Form Data:**
  - `front_file`: `<Binary Image>`
  - `back_file`: `<Binary Image>`
- **Response:** Trả về đầy đủ cả thông tin mặt trước lẫn ngày cấp, nơi cấp, đặc điểm nhận dạng ở mặt sau.

### 4. Lấy danh sách lịch sử
- **Endpoint:** `GET /api/v1/ocr/history?search=&document_type=&limit=20&offset=0`
- **Response:**
  ```json
  {
    "total": 45,
    "limit": 20,
    "offset": 0,
    "items": [ ... ]
  }
  ```

### 6. Cập nhật / Duyệt thông tin hồ sơ
- **Endpoint:** `PUT /api/v1/ocr/history/{record_id}`
- **Request Body (JSON):**
  ```json
  {
    "full_name": "NGUYỄN LƯƠNG AN",
    "id_number": "001205051692",
    "is_verified": 1,
    "notes": "Đã đối chiếu căn cước gốc"
  }
  ```

### 7. Xóa hồ sơ
- **Endpoint:** `DELETE /api/v1/ocr/history/{record_id}`

### 8. Lấy chỉ số thống kê Dashboard
- **Endpoint:** `GET /api/v1/ocr/stats`
- **Response:**
  ```json
  {
    "total_scans": 128,
    "today_scans": 14,
    "average_confidence": 0.935,
    "average_processing_time_sec": 1.82,
    "distribution_by_type": {
      "CCCD_CHIP": 92,
      "CMND_12": 26,
      "CMND_9": 10
    },
    "recent_daily_trends": [
      { "date": "2026-10-13", "count": 12 },
      { "date": "2026-10-19", "count": 14 }
    ]
  }
  ```

### 9. Xuất file Excel / CSV
- `GET /api/v1/ocr/export?format=xlsx` -> Tải file Excel.
- `GET /api/v1/ocr/export?format=csv` -> Tải file CSV.

---

## 4. TYPESCRIPT INTERFACES ĐỊNH NGHĨA SẴN (CHO FRONTEND)

```typescript
export interface FieldDetail {
  value: string | null;
  confidence: number;
}

export interface ExtractedFields {
  id_number: FieldDetail;
  full_name: FieldDetail;
  date_of_birth: FieldDetail;
  gender: FieldDetail;
  nationality: FieldDetail;
  place_of_origin: FieldDetail;
  place_of_residence: FieldDetail;
  date_of_expiry: FieldDetail;
  date_of_issue?: FieldDetail;
  issuing_authority?: FieldDetail;
  identifying_features?: FieldDetail;
  mrz_code?: FieldDetail;
}

export interface BoundingBox {
  box: number[][]; // [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
  text: string;
  confidence: number;
}

export interface OCRScanResponse {
  id: string;
  created_at: string;
  document_type: 'CCCD_CHIP' | 'CCCD_BARCODE' | 'CMND_12' | 'CMND_9' | 'UNKNOWN';
  side: 'FRONT' | 'BACK' | 'BOTH';
  overall_confidence: number;
  processing_time_sec: number;
  fields: ExtractedFields;
  warnings: string[];
  image_url?: string;
  image_back_url?: string;
  detected_boxes?: BoundingBox[];
  raw_texts?: string[];
}

export interface DashboardStats {
  total_scans: number;
  today_scans: number;
  average_confidence: number;
  average_processing_time_sec: number;
  distribution_by_type: Record<string, number>;
  recent_daily_trends: { date: string; count: number }[];
}
```
