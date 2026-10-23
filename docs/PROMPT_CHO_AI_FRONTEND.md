# 🚀 PROMPT COPY & PASTE CHO AI LÀM GIAO DIỆN FRONTEND

> **HƯỚNG DẪN DÀNH CHO BẠN:**  
> Bạn chỉ cần copy toàn bộ nội dung trong khung bên dưới và gửi cho bất kỳ AI nào (Claude 3.5 Sonnet, GPT-4o, v.v.) để AI đó lập trình ra bộ giao diện Frontend React + Tailwind CSS hoàn chỉnh, đẹp lộng lẫy và nối trực tiếp với Backend FastAPI của bạn!

---

```markdown
Bạn là một Senior Frontend Architect và UI/UX Designer xuất sắc. Tôi đã có sẵn Backend FastAPI hoàn chỉnh đang chạy tại `http://localhost:8000`, đã test 100% các API nhận diện và trích xuất ký tự quang học (OCR) cho Căn cước công dân (CCCD có chip, CCCD mã vạch) và Chứng minh nhân dân (CMND 9 số, 12 số).

Hãy giúp tôi xây dựng trọn vẹn mã nguồn Frontend cho dự án này trên nền tảng PC / Laptop (không làm Mobile App), với phong cách thiết kế eKYC FinTech cực kỳ đẹp mắt, hiện đại, mượt mà (Dark Mode sang trọng phong cách ngân hàng quốc tế, viền kính mờ glassmorphism, animation quét thẻ laser sống động).

### 1. TECH STACK ĐỀ XUẤT:
- Framework: React (Vite) + Tailwind CSS
- Icons: Lucide React hoặc FontAwesome
- Biểu đồ: Recharts hoặc Chart.js
- Animations: Framer Motion
- HTTP Client: Axios hoặc Fetch API
- Xử lý Webcam PC: Native HTML5 `navigator.mediaDevices.getUserMedia`

### 2. CÁC TÍNH NĂNG VÀ MÀN HÌNH BẮT BUỘC:

#### MÀN HÌNH 1: QUÉT QUA WEBCAM MÁY TÍNH (LIVE WEBCAM SCANNER - TRỌNG TÂM)
- Mở luồng video trực tiếp từ Webcam PC (độ phân giải 1080p hoặc 720p).
- Có khung căn chỉnh thẻ CCCD (Card Bounding Guide) chuẩn tỷ lệ vàng 1.586 : 1 với 4 góc bo sáng dạ quang và vệt quét Laser chạy lên xuống.
- Nút "Bật/Tắt Webcam", Dropdown chọn mặt thẻ (Tự động / Mặt trước / Mặt sau).
- Nút "Chụp & Quét OCR (Snapshot)":
  + Chụp frame từ video stream đưa vào canvas -> chuyển thành Base64.
  + Gửi POST `http://localhost:8000/api/v1/ocr/scan-webcam` với body:
    `{ "image_base64": "data:image/jpeg;base64,...", "side_hint": "auto" }`
  + Hiển thị trạng thái Loading Skeleton mượt mà trong khi chờ backend xử lý.

#### MÀN HÌNH 2: TẢI ẢNH FILE & DỮ LIỆU MẪU
- Vùng Drag & Drop tải file ảnh (JPG, PNG, JPEG).
- Hỗ trợ quét 1 mặt (POST `/api/v1/ocr/scan`) hoặc kéo thả cùng lúc 2 mặt trước + sau (POST `/api/v1/ocr/scan-both`).
- Khung chạy thử Dữ liệu mẫu (POST `/api/v1/ocr/demo-sample` với `sample_index=0..47`).

#### MÀN HÌNH 3: BẢNG KẾT QUẢ TRÍCH XUẤT (RESULT INSPECTOR)
- Bố cục 2 cột (Side-by-side):
  + Cột trái: Ảnh thẻ vừa chụp/tải lên, có vẽ Bounding Boxes quanh các đoạn chữ nhận diện.
  + Cột phải: Form thông tin trích xuất chi tiết có thể chỉnh sửa:
    * Số CCCD/CMND (font to, viền sáng, nút Copy 1-click có Toast thông báo)
    * Họ và tên (chữ hoa in đậm nổi bật)
    * Ngày sinh, Giới tính, Quốc tịch
    * Quê quán, Nơi thường trú
    * Có giá trị đến (ngày hết hạn)
    * Mặt sau: Ngày cấp, Nơi cấp, Đặc điểm nhận dạng
    * Badge độ tin cậy: Xanh lá (>= 85%), Vàng (60-84%), Đỏ (< 60%)
    * Nút "Lưu xác thực" (gọi PUT `/api/v1/ocr/history/{id}`)
    * Nút "Xuất file JSON"

#### MÀN HÌNH 4: BẢNG LỊCH SỬ & QUẢN LÝ (HISTORY TABLE)
- Bảng lịch sử các lần quét, có tìm kiếm tức thời theo Tên/Số CCCD/Địa chỉ (GET `/api/v1/ocr/history?search=...`).
- Bộ lọc theo loại thẻ, phân trang.
- Nút "Xuất Excel (.xlsx)" (tải từ `http://localhost:8000/api/v1/ocr/export?format=xlsx`).
- Nút "Xuất CSV" (tải từ `http://localhost:8000/api/v1/ocr/export?format=csv`).
- Nút Xem chi tiết hồ sơ, Xóa hồ sơ (DELETE `/api/v1/ocr/history/{id}`).

#### MÀN HÌNH 5: THỐNG KÊ DASHBOARD (ANALYTICS)
- 4 thẻ KPI: Tổng lượt scan, Scan hôm nay, Độ tin cậy trung bình, Thời gian xử lý trung bình (lấy từ GET `/api/v1/ocr/stats`).
- Biểu đồ tròn: Tỷ lệ loại thẻ (CCCD gắn chip, CMND 12 số, CMND 9 số).
- Biểu đồ đường/miền: Xu hướng số lượt quét 7 ngày qua.

### 3. YÊU CẦU ĐẦU RA:
Hãy cung cấp trọn vẹn cấu trúc dự án React Vite:
1. `package.json` với đầy đủ dependencies.
2. `vite.config.js` và `tailwind.config.js`.
3. Mã nguồn chi tiết các components:
   - `Navbar.jsx` / `Sidebar.jsx`
   - `WebcamScanner.jsx` (Live video feed + Canvas snapshot + Bounding overlay)
   - `FileUploadScanner.jsx`
   - `ResultCard.jsx`
   - `HistoryTable.jsx`
   - `DashboardStats.jsx`
   - `App.jsx`
4. Hướng dẫn chạy: `npm install` và `npm run dev`.
Code phải hoàn chỉnh, không dùng placeholder `// todo`, không viết tắt!
```
