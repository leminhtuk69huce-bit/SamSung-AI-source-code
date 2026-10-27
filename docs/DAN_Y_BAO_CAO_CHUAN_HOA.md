# DÀN Ý BÁO CÁO KHOA HỌC CHUẨN HÓA & GỢI Ý NỘI DUNG TOÀN DIỆN
## DỰ ÁN: SAMSUNG INNOVATION CAMPUS (SIC) AI CAPSTONE PROJECT
### Đề tài: Hệ thống AI OCR Nhận diện & Trích xuất Thông tin Thẻ Căn cước công dân / CMND Việt Nam
### Quy chuẩn độ dài toàn báo cáo: 30 - 40 trang

---

## 1. PHÂN TÍCH CÁC ĐIỂM CHƯA HỢP LÝ TRONG DÀN BÀI 11 CHƯƠNG CŨ

Trong bản nháp liệt kê ban đầu của bạn:
```
Chương 1: Giới thiệu đề tài (1.2: Phạm vi)
Chương 2: Công nghệ sử dụng
Chương 4: Dữ liệu nguồn (thiếu Chương 3)
Chương 5: Quy trình xử lý
Chương 6: Kết quả
Chương 7: Đánh giá
Chương 8: Kiểm tra độ chính xác
Chương 9: Hạn chế
Chương 10: Định hướng
Chương 11: Nguồn
```

### Các lỗi cấu trúc học thuật nghiêm trọng:
1. **Chia quá nhiều chương vụn vặt (11 chương)**: Với độ dài 30 - 40 trang, nếu chia 11 chương thì trung bình mỗi chương chỉ dài từ 1.5 - 2 trang. Điều này khiến báo cáo bị **manh mún, thiếu chiều sâu học thuật** và vi phạm trực tiếp quy chuẩn cấu trúc luận văn / đồ án của SIC và các trường đại học.
2. **Lẫn lộn giữa cấp độ "Chương" (Chapter) và "Mục/Tiểu mục" (Section/Subsection)**:
   - *"Dữ liệu nguồn"*, *"Quy trình xử lý"* chỉ là các bước kỹ thuật bên trong quá trình thực nghiệm, không thể đứng độc lập thành một Chương.
   - *"Kết quả"*, *"Đánh giá"*, *"Kiểm tra độ chính xác"* bản chất là **cùng một nhóm nội dung** (Chương Đánh giá & Thực nghiệm). Tách rời chúng thành 3 chương riêng biệt sẽ gây lặp nội dung và loãng cấu trúc.
   - *"Hạn chế"*, *"Định hướng"* thực chất là các tiểu mục bắt buộc thuộc **Phần Kết luận**.
   - *"Nguồn"* chính là danh mục **Tài liệu tham khảo (References)**, tuyệt đối không được đánh số là "Chương 11".
3. **Bỏ sót các phần sống còn của một đồ án kỹ thuật phần mềm & AI**:
   - Thiếu phần **Phân tích yêu cầu hệ thống** (Yêu cầu chức năng, phi chức năng).
   - Thiếu phần **Mô hình hóa hệ thống & Ca sử dụng (Use Case Analysis)**.
   - Thiếu phần **Thiết kế kiến trúc phân tầng (Architecture Design)** và **Thiết kế CSDL (Database Design)**.
   - Thiếu phần **Đặc tả thuật toán Heuristics bóc tách tiếng Việt** (vũ khí quyết định độ chính xác cao của hệ thống).

---

## 2. BẢNG ÁNH XẠ (MAPPING) TỪ DÀN BÀI CŨ SANG KHUNG CHUẨN 4 CHƯƠNG

Dưới đây là sơ đồ gom nhóm và sắp xếp lại toàn bộ các ý của bạn vào đúng vị trí chuẩn mực:

| Nội dung cũ bạn liệt kê | Cấp độ thực tế | Vị trí chuẩn trong báo cáo chính thức | Lý do sắp xếp lại |
| :--- | :---: | :--- | :--- |
| **Chương 1: Giới thiệu đề tài (1.2 Phạm vi)** | Phần Mở đầu | **ĐẶT VẤN ĐỀ / MỞ ĐẦU** (Tính cấp thiết, Mục tiêu, Đối tượng, Phạm vi) | Đây là phần mở đầu dẫn dắt người đọc, nằm trước Chương 1 lý thuyết. |
| **Chương 2: Công nghệ sử dụng** | Chương lớn | **CHƯƠNG 1: CƠ SỞ LÝ THUYẾT & CÔNG NGHỆ LIÊN QUAN** | Cung cấp nền tảng lý thuyết: Deep Learning, OCR (CRAFT, CRNN), FastAPI, OpenCV. |
| *(Mục mới bổ sung)* | Chương lớn | **CHƯƠNG 2: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG** | Yêu cầu bài toán, 5 Use Cases cốt lõi, kiến trúc 4 tầng, sequence diagram, CSDL SQLite, UI/UX. |
| **Chương 4: Dữ liệu nguồn**<br>**Chương 5: Quy trình xử lý** | Các mục chính | **CHƯƠNG 3: HUẤN LUYỆN MÔ HÌNH VÀ TÍCH HỢP HỆ THỐNG**<br>- 3.1. Dữ liệu nguồn & Tiền xử lý<br>- 3.2. Cấu hình mô hình OCR<br>- 3.3. Thuật toán bóc tách Heuristics tiếng Việt<br>- 3.4. Tích hợp hệ thống Backend/Frontend | Ghép vào quy trình xây dựng hệ thống hoàn chỉnh từ dữ liệu $\rightarrow$ thuật toán $\rightarrow$ tích hợp. |
| **Chương 6: Kết quả**<br>**Chương 7: Đánh giá**<br>**Chương 8: Kiểm tra độ chính xác** | Các mục chính | **CHƯƠNG 4: KẾT QUẢ, KIỂM THỬ VÀ ĐÁNH GIÁ HỆ THỐNG**<br>- 4.1. Kịch bản kiểm thử (10 Test Cases)<br>- 4.2. Kết quả nhận diện trên giao diện<br>- 4.3. Đánh giá độ chính xác (Precision/Recall/F1)<br>- 4.4. Đo đạc hiệu năng CPU/GPU & Phân tích lỗi | Gộp chung thành một chương thực nghiệm khoa học, có số liệu đối chứng chặt chẽ. |
| **Chương 9: Hạn chế**<br>**Chương 10: Định hướng** | Các mục con | **KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN**<br>- 5.1. Kết luận những việc đã làm được<br>- 5.2. Các mặt hạn chế còn tồn tại<br>- 5.3. Định hướng phát triển tương lai | Tiêu chuẩn kết bài của mọi báo cáo khoa học. |
| **Chương 11: Nguồn** | Mục độc lập | **TÀI LIỆU THAM KHẢO (REFERENCES)** | Đặt ở cuối báo cáo, định dạng theo chuẩn trích dẫn khoa học (IEEE hoặc APA). |

---

## 3. KHUNG DÀN Ý CHI TIẾT ĐỀ XUẤT CHO BÁO CÁO (30 - 40 TRANG)

### TRANG BÌA & CÁC TRANG MỞ ĐẦU (1 - 2 trang)
- Trang bìa chính thức: Tên trường, Tên chương trình Samsung Innovation Campus (SIC), Tên đề tài, Giảng viên hướng dẫn, Nhóm sinh viên thực hiện.
- Lời cảm ơn (Acknowlegements)
- Tóm tắt đề tài (Abstract - Tiếng Việt & Tiếng Anh)
- Mục lục (Table of Contents)
- Danh mục các ký hiệu và chữ viết tắt (Abbreviations: OCR, CCCD, CMND, eKYC, CRAFT, CRNN, CTC, API...)
- Danh mục hình vẽ và bảng biểu (List of Figures & Tables)

---

### PHẦN ĐẶT VẤN ĐỀ / MỞ ĐẦU (2 - 3 trang)
1. **Lý do chọn đề tài & Tính cấp thiết**:
   - Sự bùng nổ của chuyển đổi số quốc gia và nhu cầu định danh điện tử (eKYC) trong ngân hàng, hành chính công, dịch vụ số.
   - Hạn chế của việc nhập liệu thủ công (chậm, sai sót số định danh, sai dấu tiếng Việt).
   - Nhu cầu về một giải pháp AI OCR chạy độc lập (Offline / On-Premise), bảo mật dữ liệu công dân, phản hồi nhanh dưới 2 giây.
2. **Mục tiêu nghiên cứu**:
   - Mục tiêu tổng quát: Xây dựng hệ thống phần mềm hoàn chỉnh nhận diện và trích xuất tự động thông tin trên thẻ CCCD/CMND Việt Nam.
   - Mục tiêu cụ thể: Độ chính xác trường dữ liệu cốt lõi $\ge 95\%$, thời gian xử lý $\le 2.0$ giây trên CPU thông thường, giao diện trực quan hỗ trợ Human-in-the-Loop.
3. **Đối tượng và phạm vi nghiên cứu**:
   - Đối tượng: Các mẫu giấy tờ tùy thân Việt Nam (CCCD gắn chip, CCCD mã vạch, CMND 12 số, CMND 9 số; gồm cả mặt trước và mặt sau).
   - Phạm vi nghiên cứu: Xử lý ảnh chụp từ camera điện thoại, webcam và tệp scan; triển khai trên môi trường Windows và Ubuntu Linux.
4. **Phương pháp nghiên cứu**:
   - Phương pháp kết hợp: Thị giác máy tính tiền xử lý ảnh + Mạng nơ-ron học sâu (Deep Learning) nhận dạng ký tự + Hệ chuyên gia luật (Rule-based & Heuristics) chuẩn hóa dữ liệu tiếng Việt.
5. **Bố cục báo cáo**: Tóm tắt nội dung 4 chương tiếp theo.

---

### CHƯƠNG 1: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ LIÊN QUAN (6 - 8 trang)
*Mục đích: Cung cấp nền tảng khoa học và công nghệ làm cơ sở triển khai hệ thống.*

1. **1.1. Tổng quan về công nghệ nhận dạng ký tự quang học (OCR)**:
   - Lịch sử phát triển: Từ OCR truyền thống (Tesseract, template matching) đến Deep Learning OCR.
   - Các thách thức đặc thù của tiếng Việt: Hệ thống 89 chữ cái có dấu thanh (sắc, huyền, hỏi, ngã, nặng) dễ bị mất nét khi chất lượng ảnh kém.
2. **1.2. Chuẩn thẻ Căn cước công dân và Chứng minh nhân dân Việt Nam**:
   - Kích thước chuẩn quốc tế ISO/IEC 7810 ID-1 ($85.60 \times 53.98\text{ mm}$).
   - Quy luật 12 chữ số trên CCCD: 3 số đầu (mã tỉnh), số thứ 4 (thế kỷ và giới tính), 2 số tiếp theo (năm sinh), 6 số cuối (số ngẫu nhiên).
   - Mã đọc máy MRZ (Machine Readable Zone) mặt sau chuẩn ICAO Doc 9303 TD1 (3 dòng $\times$ 30 ký tự).
3. **1.3. Các kỹ thuật thị giác máy tính và tiền xử lý hình ảnh**:
   - Thuật toán cân bằng độ tương phản thích nghi CLAHE.
   - Bộ lọc làm sắc nét viền chữ Unsharp Masking.
   - Phát hiện biên cạnh Canny và biến đổi phối cảnh Perspective Transform để nắn phẳng thẻ.
4. **1.4. Kiến trúc học sâu phát hiện vùng văn bản (CRAFT)**:
   - Nguyên lý Character Region Awareness for Text Detection.
   - Điểm liên kết ký tự (Affinity Score) và Điểm vùng ký tự (Region Score).
5. **1.5. Kiến trúc học sâu nhận dạng chuỗi văn bản (CRNN/BiLSTM + CTC)**:
   - Trích xuất đặc trưng hình ảnh bằng CNN (ResNet/VGG).
   - Mô hình hóa ngữ cảnh chuỗi ký tự bằng Bi-directional LSTM.
   - Hàm mất mát Connectionist Temporal Classification (CTC Loss) giải quyết bài toán chuỗi không cần căn chỉnh nhãn.
6. **1.6. Công nghệ phát triển phần mềm và môi trường thực thi**:
   - Thư viện EasyOCR (mô hình tối ưu cho tiếng Việt và Latin).
   - Framework backend FastAPI (bất đồng bộ, OpenAPI Swagger).
   - Hệ quản trị CSDL SQLite (nhẹ, chuẩn ACID, nhúng cục bộ).
   - Giao diện người dùng Web Vanilla SPA (HTML5/CSS3/ES6).

---

### CHƯƠNG 2: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG (8 - 12 trang)
*Mục đích: Thiết kế kiến trúc tổng thể, mô hình hóa chức năng và cơ sở dữ liệu.*

1. **2.1. Phân tích yêu cầu hệ thống**:
   - Yêu cầu chức năng (FR-01 đến FR-06): Tải ảnh/chụp webcam 2 giai đoạn, tiền xử lý, bóc tách 12 trường, kiểm duyệt Human-in-the-Loop, tra cứu lịch sử, xuất báo cáo.
   - Yêu cầu phi chức năng (NFR): Tốc độ $\le 2.5$s CPU, bảo mật On-Premise, độ chính xác cao, tính khả dụng.
2. **2.2. Phân tích Ca sử dụng (Use Case Analysis)**:
   - Xác định 3 tác nhân: Người dùng, AI OCR Engine, SQLite Database.
   - Biểu đồ Use Case tổng thể theo chuẩn User-Goal Level (5 Use Cases cốt lõi: UC-01 đến UC-05).
   - Bảng đặc tả chi tiết từng Use Case (Mục tiêu, tiền điều kiện, luồng sự kiện, hậu điều kiện).
3. **2.3. Thiết kế kiến trúc hệ thống (System Architecture Design)**:
   - Mô hình kiến trúc phân tầng Clean Architecture 4 lớp: Presentation Layer $\rightarrow$ API Routing Layer $\rightarrow$ Business & AI Services Layer $\rightarrow$ Persistence Layer.
   - Sơ đồ Pipeline xử lý dữ liệu AI OCR từ đầu vào đến đầu ra (End-to-End Pipeline).
4. **2.4. Thiết kế động - Biểu đồ tuần tự (Sequence Diagrams)**:
   - Biểu đồ tuần tự UC-01: Luồng Quét và Trích xuất thông tin thẻ (Webcam / Upload).
   - Biểu đồ tuần tự UC-02: Luồng Kiểm duyệt, Sửa trực tiếp, Lưu CSDL và Tự động xuất JSON.
5. **2.5. Thiết kế Cơ sở dữ liệu (Database Design)**:
   - Sơ đồ thực thể quan hệ (ERD).
   - Từ điển dữ liệu chi tiết bảng `ocr_records` (21 trường dữ liệu).
   - Chiến lược lập chỉ mục (Indexing) trên `id_number`, `full_name`, `created_at`.
6. **2.6. Thiết kế Giao diện Người dùng (UI/UX Design)**:
   - Bố cục 2 cột Side-by-side (Trái: Khung chụp/upload; Phải: Biểu mẫu trích xuất).
   - Khung ngắm tỷ lệ thẻ chuẩn ISO/IEC 7810 ID-1 kèm góc neon.
   - Quy trình chụp webcam 2 giai đoạn (Chụp $\rightarrow$ Đóng băng xem trước $\rightarrow$ Gửi quét).
   - Tương tác Bounding Boxes đa chiều (Hover đồng bộ giữa ảnh và ô input).

---

### CHƯƠNG 3: HUẤN LUYỆN MÔ HÌNH VÀ TÍCH HỢP HỆ THỐNG (7 - 9 trang)
*Mục đích: Hiện thực hóa thuật toán, tối ưu mã nguồn và tích hợp các module.*

1. **3.1. Dữ liệu nguồn và quy trình xử lý dữ liệu**:
   - Nguồn dữ liệu thực nghiệm: Tập ảnh mẫu các loại thẻ CCCD/CMND đa dạng điều kiện chụp (đủ sáng, thiếu sáng, góc nghiêng, bóng mờ).
   - Quy trình gán nhãn dữ liệu và bảo mật thông tin cá nhân.
2. **3.2. Cấu hình và tối ưu hóa mô hình AI OCR**:
   - Áp dụng Singleton Pattern cho EasyOCR Reader (khởi tạo 1 lần duy nhất khi server startup, tránh re-init).
   - Đóng gói trọng số ngoại tuyến (`craft_mlt_25k.pth`, `latin_g2.pth`) đảm bảo ứng dụng chạy 100% không cần Internet.
   - Xử lý bất đồng bộ CPU-bound qua `run_in_threadpool` để giải phóng Event Loop của FastAPI.
3. **3.3. Các thuật toán tiền xử lý hình ảnh tối ưu**:
   - Thuật toán co giãn ảnh thích nghi (Adaptive Resizing) về cạnh dài chuẩn 1280px - 1600px.
   - Kết hợp CLAHE và Unsharp Masking để khôi phục các dấu thanh tiếng Việt bị đứt nét.
   - Thuật toán tự động tìm 4 góc và nắn thẳng phối cảnh thẻ.
4. **3.4. Các thuật toán Heuristics bóc tách và chuẩn hóa thông tin**:
   - Thuật toán gom nhóm dòng văn bản theo trục tọa độ Y (`group_boxes_into_lines`).
   - Thuật toán Multi-date Heuristic phân định chuẩn xác Ngày sinh ($\le 2024$) và Hạn dùng ($\ge 2025$ / "Không thời hạn").
   - Thuật toán chuẩn hóa ký tự nhầm lẫn chữ-số (`O` $\rightarrow$ `0`, `I` $\rightarrow$ `1`, `B` $\rightarrow$ `8`...).
   - Thuật toán suy luận Giới tính qua chữ số thứ 4 của mã CCCD 12 số (độ tin cậy $95\%$).
   - Thuật toán làm sạch địa chỉ và khớp từ điển chuẩn 63 Tỉnh/Thành phố Việt Nam.
   - Thuật toán tự động tái tạo chuỗi MRZ 3 dòng chuẩn ICAO Doc 9303 TD1.
5. **3.5. Tích hợp hệ thống Backend - Frontend**:
   - Xây dựng các RESTful API endpoints: `/api/v1/ocr/scan`, `/scan-webcam`, `/history`, `/export`.
   - Cơ chế tự động kích hoạt tải file JSON ngay khi người dùng bấm "Xác nhận & Lưu".
6. **3.6. Đóng gói và triển khai đa nền tảng**:
   - Bản Windows: Đóng gói Portable EXE độc lập.
   - Bản Ubuntu/Linux: Script tự động hóa (`setup_ubuntu.sh`, `run.sh`) và container hóa qua Docker (`Dockerfile`, `docker-compose.yml`).

---

### CHƯƠNG 4: KẾT QUẢ, KIỂM THỬ VÀ ĐÁNH GIÁ HỆ THỐNG (6 - 8 trang)
*Mục đích: Chứng minh tính đúng đắn, đo lường độ chính xác và tốc độ thực tế của hệ thống.*

1. **4.1. Môi trường thực nghiệm và Kịch bản kiểm thử**:
   - Cấu hình phần cứng và phần mềm thử nghiệm (CPU Intel Core i5/i7, RAM 8GB-16GB, OS Windows 11 & Ubuntu 22.04).
   - Kịch bản kiểm thử tự động toàn diện: 10 Test Cases kiểm tra từ API gốc, Health check, OCR file ảnh, OCR webcam Base64, CRUD lịch sử đến xuất báo cáo Excel/CSV (Tất cả đạt 100% PASSED).
2. **4.2. Kết quả giao diện và chức năng thực tế**:
   - Ảnh chụp minh chứng giao diện màn hình quét thẻ (Webcam live stream, khung ngắm ID-1).
   - Ảnh chụp minh chứng kết quả bóc tách song song Side-by-side và Bounding Boxes hiển thị trên ảnh.
   - Ảnh chụp minh chứng Modal popup xác nhận thành công và file JSON tự động tải về.
   - Ảnh chụp minh chứng trang Lịch sử, bộ lọc loại thẻ và Dashboard thống kê biểu đồ.
3. **4.3. Đánh giá độ chính xác nhận diện (Accuracy Evaluation)**:
   - Bảng thống kê độ chính xác chi tiết theo từng trường thông tin (Số CCCD, Họ tên, Ngày sinh, Giới tính, Quê quán, Thường trú, Hạn dùng).
   - So sánh các chỉ số định lượng: Precision, Recall, F1-score.
   - Đánh giá hiệu quả của thuật toán Heuristics (độ chính xác tăng từ ~84% lên trên 96% sau khi áp dụng từ điển 63 tỉnh/thành và chuẩn hóa ký tự nhầm).
4. **4.4. Đánh giá hiệu năng và thời gian đáp ứng (Performance Benchmark)**:
   - Biểu đồ thời gian xử lý trung bình theo từng công đoạn: Tiền xử lý (~0.2s) $\rightarrow$ OCR inference (~1.2s - 1.8s) $\rightarrow$ Bóc tách heuristics (~0.05s) $\rightarrow$ Tổng thời gian $\le 2.0$ giây trên CPU.
   - So sánh thời gian xử lý giữa CPU và GPU (nếu có).
   - Đánh giá mức độ chiếm dụng tài nguyên bộ nhớ (RAM ổn định ~800MB - 1.2GB nhờ mô hình Singleton).
5. **4.5. Phân tích lỗi và các ca biên (Error Analysis & Edge Cases)**:
   - Phân tích các trường hợp ảnh thẻ bị mờ nhòe nghiêm trọng, góc chụp quá nghiêng (> 45 độ), hoặc bị lóa đèn flash.
   - Vai trò cứu vãn của cơ chế kiểm duyệt Human-in-the-Loop cho phép người dùng click sửa trực tiếp.

---

### PHẦN KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN (2 - 3 trang)
1. **Kết luận những kết quả đạt được**:
   - Đã xây dựng thành công một hệ thống AI OCR hoàn chỉnh từ mô hình Deep Learning đến giao diện người dùng trực quan.
   - Bóc tách đầy đủ và chính xác 12 trường thông tin cốt lõi trên các loại thẻ CCCD/CMND Việt Nam.
   - Hệ thống vận hành độc lập (Offline), bảo mật tuyệt đối dữ liệu người dùng, triển khai mượt mà trên cả Windows và Ubuntu.
2. **Hạn chế của đề tài**:
   - Khi ảnh chụp bị mất góc nghiêm trọng hoặc bị lóa sáng che phủ chữ, mô hình vẫn cần sự can thiệp chỉnh sửa của con người.
   - Chưa tích hợp tính năng phát hiện giả mạo khuôn mặt (Facial Liveness Detection) để so khớp ảnh thẻ với khuôn mặt người cầm thẻ.
3. **Định hướng phát triển trong tương lai**:
   - Mở rộng nhận dạng thêm các loại giấy tờ tùy thân khác: Giấy phép lái xe (GPLX), Hộ chiếu (Passport), Thẻ bảo hiểm y tế (BHYT).
   - Tích hợp thêm module Face Matching đối sánh khuôn mặt trên thẻ và camera live để hoàn thiện giải pháp eKYC toàn diện.
   - Tối ưu hóa mô hình qua ONNX Runtime hoặc TensorRT để tăng tốc độ xử lý lên dưới 0.5 giây trên CPU.

---

### TÀI LIỆU THAM KHẢO (1 - 2 trang)
Trình bày theo chuẩn khoa học (IEEE hoặc APA), ví dụ:
1. Baek, Y., Lee, B., Han, D., Yun, S., & Lee, H. (2019). Character region awareness for text detection. *In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, pp. 9365-9374.
2. Shi, B., Bai, X., & Yao, C. (2016). An end-to-end trainable neural network for image-based sequence recognition and its application to scene text recognition. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 39(11), 2298-2304.
3. EasyOCR: Ready-to-use OCR with 80+ supported languages. Jaided AI. https://github.com/JaidedAI/EasyOCR.
4. Tiêu chuẩn ICAO Doc 9303: Machine Readable Travel Documents - Part 5: Specifications for TD1 Size Machine Readable Official Travel Documents.
5. Luật Căn cước số 26/2023/QH15 của Quốc hội Nước CHXHCN Việt Nam.
