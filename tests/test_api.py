import os
import sys
import base64
from pathlib import Path

# Fix Windows console UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Fix OpenMP issue & add paths
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    print("[TEST 1] Kiểm tra endpoint gốc '/'...")
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (200, 307)
    if response.status_code == 200 and "application/json" in response.headers.get("content-type", ""):
        data = response.json()
        assert data.get("status") == "online"
    print(" -> Root API: PASSED")


def test_health():
    print("[TEST 2] Kiểm tra endpoint '/api/v1/health'...")
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print(f" -> Health: PASSED (Số mẫu có sẵn: {data['total_sample_cases_available']})")

def test_stats_initial():
    print("[TEST 3] Kiểm tra endpoint '/api/v1/ocr/stats'...")
    response = client.get("/api/v1/ocr/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_scans" in data
    print(f" -> Stats: PASSED (Tổng lượt scan hiện tại: {data['total_scans']})")

def test_demo_sample_ocr():
    print("[TEST 4] Kiểm tra OCR trích xuất từ dữ liệu mẫu '/api/v1/ocr/demo-sample'...")
    response = client.post("/api/v1/ocr/demo-sample", data={"sample_index": 0})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "fields" in data
    record_id = data["id"]
    fields = data["fields"]
    print(f" -> Demo Sample OCR: PASSED (ID: {record_id})")
    print(f"    - Loại thẻ: {data.get('document_type')}")
    print(f"    - Số CCCD: {fields.get('id_number', {}).get('value')}")
    print(f"    - Họ tên: {fields.get('full_name', {}).get('value')}")
    print(f"    - Ngày sinh: {fields.get('date_of_birth', {}).get('value')}")
    print(f"    - Độ tin cậy: {data.get('overall_confidence')}")
    return record_id

def test_history_list(record_id: str):
    print("[TEST 5] Kiểm tra lấy danh sách lịch sử '/api/v1/ocr/history'...")
    response = client.get("/api/v1/ocr/history?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
    print(f" -> History List: PASSED (Tìm thấy {data['total']} bản ghi)")

def test_history_detail(record_id: str):
    print(f"[TEST 6] Kiểm tra lấy chi tiết bản ghi '/api/v1/ocr/history/{record_id}'...")
    response = client.get(f"/api/v1/ocr/history/{record_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["id"] == record_id
    print(" -> History Detail: PASSED")

def test_history_update(record_id: str):
    print(f"[TEST 7] Kiểm tra cập nhật thông tin '/api/v1/ocr/history/{record_id}'...")
    payload = {
        "full_name": "NGUYỄN VĂN A (ĐÃ DUYỆT)",
        "is_verified": 1,
        "notes": "Đã kiểm tra đối chiếu gốc"
    }
    response = client.put(f"/api/v1/ocr/history/{record_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["full_name"] == "NGUYỄN VĂN A (ĐÃ DUYỆT)"
    assert data["data"]["is_verified"] == 1
    print(" -> History Update: PASSED")

def test_export():
    print("[TEST 8] Kiểm tra xuất file Excel & CSV '/api/v1/ocr/export'...")
    # CSV
    res_csv = client.get("/api/v1/ocr/export?format=csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    assert len(res_csv.content) > 50

    # Excel
    res_xlsx = client.get("/api/v1/ocr/export?format=xlsx")
    assert res_xlsx.status_code == 200
    assert len(res_xlsx.content) > 100
    print(" -> Export CSV & Excel: PASSED")

def test_webcam_scan():
    print("[TEST 9] Kiểm tra API Webcam scan (Base64) '/api/v1/ocr/scan-webcam'...")
    # Create a small valid test image in base64
    import numpy as np
    import cv2
    dummy_img = np.zeros((300, 500, 3), dtype=np.uint8)
    cv2.putText(dummy_img, "001205051692", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(dummy_img, "NGUYEN VAN A", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    _, buffer = cv2.imencode(".jpg", dummy_img)
    b64_str = "data:image/jpeg;base64," + base64.b64encode(buffer).decode("utf-8")

    payload = {
        "image_base64": b64_str,
        "side_hint": "front"
    }
    response = client.post("/api/v1/ocr/scan-webcam", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    print(" -> Webcam Scan (Base64): PASSED")
    return data["id"]

def test_delete(record_id: str):
    print(f"[TEST 10] Kiểm tra xóa bản ghi '/api/v1/ocr/history/{record_id}'...")
    response = client.delete(f"/api/v1/ocr/history/{record_id}")
    assert response.status_code == 200
    print(" -> Delete: PASSED")

if __name__ == "__main__":
    print("=" * 60)
    print("BẮT ĐẦU CHẠY KIỂM THỬ TOÀN DIỆN BACKEND OCR API...")
    print("=" * 60)
    test_root()
    test_health()
    test_stats_initial()
    rec_id = test_demo_sample_ocr()
    test_history_list(rec_id)
    test_history_detail(rec_id)
    test_history_update(rec_id)
    test_export()
    webcam_rec_id = test_webcam_scan()
    test_delete(webcam_rec_id)
    print("=" * 60)
    print("🎉 TẤT CẢ 10/10 TEST CASES ĐÃ PASS 100% THÀNH CÔNG!")
    print("=" * 60)
