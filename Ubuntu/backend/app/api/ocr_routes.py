import time
import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from starlette.concurrency import run_in_threadpool
from ..config import STORAGE_DIR, TARGET_IMAGE_WIDTH
from ..schemas import OCRScanResponse, WebcamScanRequest, WebcamBothScanRequest, BoundingBox, FieldDetail
from ..services.preprocessor import (
    read_image_from_bytes,
    read_image_from_base64,
    read_image_from_path,
    auto_orient_card,
    resize_for_ocr,
    enhance_image,
    save_image_to_storage
)
from ..services.card_detector import detect_and_crop_card
from ..services.ocr_engine import get_ocr_engine
from ..services.extractor import extract_fields, merge_front_and_back
from ..database import save_record

router = APIRouter(prefix="/api/v1/ocr", tags=["OCR Processing"])

def process_single_image(image_bytes: bytes, filename_prefix: str = "scan", side_hint: str = "auto") -> tuple:
    """Core helper to process an image array, run OCR and extract fields."""
    start_time = time.time()

    # 1. Read raw image
    image = read_image_from_bytes(image_bytes)

    # 2. [CARD DETECT] Phát hiện và crop vùng thẻ CCCD trước khi OCR
    image, card_found = detect_and_crop_card(image)

    # 3. Auto-orient (theo mã QR), resize & enhance
    image, _ = auto_orient_card(image)
    resized, scale = resize_for_ocr(image, target_width=TARGET_IMAGE_WIDTH)
    enhanced = enhance_image(resized)

    # 4. Run OCR
    engine = get_ocr_engine()
    raw_boxes = engine.run_ocr(enhanced)

    # 5. Extract Fields
    extracted = extract_fields(raw_boxes, side_hint=side_hint)
    if not card_found:
        extracted.setdefault("warnings", []).append(
            "Không xác định khung viền CCCD, vui lòng chụp lại với đầy đủ ánh sáng và không để vật cản."
        )
    elapsed = round(time.time() - start_time, 2)

    # 6. Save image to storage safely
    record_id = str(uuid.uuid4())
    img_name = f"{filename_prefix}_{record_id}.jpg"
    img_path = STORAGE_DIR / img_name
    saved_path = save_image_to_storage(image, img_path)
    img_url = f"/storage/{img_name}" if saved_path else None

    return record_id, extracted, raw_boxes, elapsed, img_url

def process_webcam_image(image_base64: str, side_hint: str = "auto") -> tuple:
    """Core helper to decode base64 webcam frame, run OCR and extract fields."""
    start_time = time.time()
    image = read_image_from_base64(image_base64)

    # [CARD DETECT] Phát hiện và crop vùng thẻ CCCD trước khi OCR
    image, card_found = detect_and_crop_card(image)

    image, _ = auto_orient_card(image)
    resized, scale = resize_for_ocr(image, target_width=TARGET_IMAGE_WIDTH)
    enhanced = enhance_image(resized)

    engine = get_ocr_engine()
    raw_boxes = engine.run_ocr(enhanced)
    extracted = extract_fields(raw_boxes, side_hint=side_hint)
    if not card_found:
        extracted.setdefault("warnings", []).append(
            "Khong tu dong xac dinh duoc vung the. Hay dat the CCCD ro rang, du anh sang."
        )
    elapsed = round(time.time() - start_time, 2)

    record_id = str(uuid.uuid4())
    img_name = f"webcam_{record_id}.jpg"
    img_path = STORAGE_DIR / img_name
    saved_path = save_image_to_storage(image, img_path)
    img_url = f"/storage/{img_name}" if saved_path else None

    return record_id, extracted, raw_boxes, elapsed, img_url

@router.post("/scan", response_model=OCRScanResponse, summary="Quét ảnh CCCD/CMND tải lên (File upload)")
async def scan_file(
    file: Optional[UploadFile] = File(None, description="File ảnh thẻ CCCD/CMND (JPG, PNG, JPEG)"),
    side_hint: Optional[str] = Form("auto", description="Gợi ý mặt thẻ: front | back | auto"),
    request: Request = None
):
    valid_exts = (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff")
    content = None
    chosen_side = (side_hint or "auto").upper()

    # Thử lấy content từ UploadFile
    if file is not None:
        try:
            content = await file.read()
        except Exception:
            content = None

    # Nếu chưa có content hoặc request gửi JSON Base64
    if not content and request is not None:
        try:
            c_type = request.headers.get("content-type", "").lower()
            if "application/json" in c_type:
                import base64 as b64
                body = await request.json()
                b64_str = body.get("image_base64") or body.get("file") or body.get("image") or ""
                if "," in b64_str: b64_str = b64_str.split(",", 1)[-1]
                if b64_str: content = b64.b64decode(b64_str)
                if body.get("side_hint"): chosen_side = body.get("side_hint").upper()
            else:
                form = await request.form()
                f_item = form.get("file")
                if f_item is not None and hasattr(f_item, "read"):
                    content = await f_item.read()
                if form.get("side_hint"):
                    chosen_side = str(form.get("side_hint")).upper()
        except Exception as parse_e:
            print(f"[SCAN] Request parse fallback: {parse_e}")

    if not content:
        raise HTTPException(status_code=400, detail="Vui lòng tải lên file định dạng hình ảnh hợp lệ (JPG, PNG, JPEG).")

    try:
        record_id, extracted, raw_boxes, elapsed, img_url = await run_in_threadpool(
            process_single_image, content, filename_prefix="upload", side_hint=chosen_side
        )

        # Prepare database payload
        fields = extracted["fields"]
        db_payload = {
            "id": record_id,
            "document_type": extracted["document_type"],
            "side": extracted["side"],
            "id_number": fields["id_number"]["value"],
            "full_name": fields["full_name"]["value"],
            "date_of_birth": fields["date_of_birth"]["value"],
            "gender": fields["gender"]["value"],
            "nationality": fields["nationality"]["value"],
            "place_of_origin": fields["place_of_origin"]["value"],
            "place_of_residence": fields["place_of_residence"]["value"],
            "date_of_expiry": fields["date_of_expiry"]["value"],
            "date_of_issue": fields["date_of_issue"]["value"],
            "issuing_authority": fields["issuing_authority"]["value"],
            "identifying_features": fields["identifying_features"]["value"],
            "mrz_code": fields["mrz_code"]["value"],
            "confidence_score": extracted["overall_confidence"],
            "processing_time_sec": elapsed,
            "image_front_path": img_url if extracted["side"] == "FRONT" else None,
            "image_back_path": img_url if extracted["side"] == "BACK" else None,
            "raw_detection_json": raw_boxes,
        }
        save_record(db_payload)

        # Map bounding boxes for frontend inspector
        boxes = [
            BoundingBox(box=b["box"], text=b["text"], confidence=round(b["confidence"], 2))
            for b in raw_boxes
        ]

        # Convert fields to FieldDetail
        field_details = {
            k: FieldDetail(value=v["value"], confidence=round(v["confidence"], 2))
            for k, v in fields.items()
        }

        return OCRScanResponse(
            id=record_id,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            document_type=extracted["document_type"],
            side=extracted["side"],
            overall_confidence=extracted["overall_confidence"],
            processing_time_sec=elapsed,
            fields=field_details,
            warnings=extracted["warnings"],
            image_url=img_url,
            detected_boxes=boxes,
            raw_texts=[b["text"] for b in raw_boxes]
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý OCR: {str(e)}")

@router.post("/scan-webcam", response_model=OCRScanResponse, summary="Quét ảnh trực tiếp từ Webcam máy tính (Base64)")
async def scan_webcam(payload: WebcamScanRequest):
    """
    Nhận diện kí tự từ ảnh chụp trực tiếp qua Webcam máy tính (chuyển sang chuỗi Base64).
    Phù hợp cho chức năng chụp ảnh live trong trình duyệt.
    """
    try:
        side_hint = payload.side_hint.upper() if payload.side_hint else "auto"
        record_id, extracted, raw_boxes, elapsed, img_url = await run_in_threadpool(
            process_webcam_image, payload.image_base64, side_hint
        )

        fields = extracted["fields"]
        db_payload = {
            "id": record_id,
            "document_type": extracted["document_type"],
            "side": extracted["side"],
            "id_number": fields["id_number"]["value"],
            "full_name": fields["full_name"]["value"],
            "date_of_birth": fields["date_of_birth"]["value"],
            "gender": fields["gender"]["value"],
            "nationality": fields["nationality"]["value"],
            "place_of_origin": fields["place_of_origin"]["value"],
            "place_of_residence": fields["place_of_residence"]["value"],
            "date_of_expiry": fields["date_of_expiry"]["value"],
            "date_of_issue": fields["date_of_issue"]["value"],
            "issuing_authority": fields["issuing_authority"]["value"],
            "identifying_features": fields["identifying_features"]["value"],
            "mrz_code": fields["mrz_code"]["value"],
            "confidence_score": extracted["overall_confidence"],
            "processing_time_sec": elapsed,
            "image_front_path": img_url if extracted["side"] == "FRONT" else None,
            "image_back_path": img_url if extracted["side"] == "BACK" else None,
            "raw_detection_json": raw_boxes,
        }
        save_record(db_payload)

        boxes = [
            BoundingBox(box=b["box"], text=b["text"], confidence=round(b["confidence"], 2))
            for b in raw_boxes
        ]
        field_details = {
            k: FieldDetail(value=v["value"], confidence=round(v["confidence"], 2))
            for k, v in fields.items()
        }

        return OCRScanResponse(
            id=record_id,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            document_type=extracted["document_type"],
            side=extracted["side"],
            overall_confidence=extracted["overall_confidence"],
            processing_time_sec=elapsed,
            fields=field_details,
            warnings=extracted["warnings"],
            image_url=img_url,
            detected_boxes=boxes,
            raw_texts=[b["text"] for b in raw_boxes]
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý OCR webcam: {str(e)}")

@router.post("/scan-webcam-both", response_model=OCRScanResponse, summary="Quét cả 2 mặt trực tiếp từ Webcam (Base64)")
async def scan_webcam_both(payload: WebcamBothScanRequest):
    """
    Nhận diện kí tự và ghép toàn diện dữ liệu từ cả 2 mặt thẻ CCCD/CMND chụp từ Webcam.
    """
    try:
        t0 = time.time()
        import base64 as b64

        front_clean = payload.front_base64.split(",", 1)[-1] if "," in payload.front_base64 else payload.front_base64
        back_clean = payload.back_base64.split(",", 1)[-1] if "," in payload.back_base64 else payload.back_base64

        front_bytes = b64.b64decode(front_clean)
        back_bytes = b64.b64decode(back_clean)

        f_id, f_extracted, f_boxes, _, f_url = await run_in_threadpool(
            process_single_image, front_bytes, "webcam_front", side_hint="FRONT"
        )
        b_id, b_extracted, b_boxes, _, b_url = await run_in_threadpool(
            process_single_image, back_bytes, "webcam_back", side_hint="BACK"
        )

        merged = merge_front_and_back(f_extracted, b_extracted)
        total_time = round(time.time() - t0, 2)

        record_id = str(uuid.uuid4())
        fields = merged["fields"]

        db_payload = {
            "id": record_id,
            "document_type": merged["document_type"],
            "side": "BOTH",
            "id_number": fields["id_number"]["value"],
            "full_name": fields["full_name"]["value"],
            "date_of_birth": fields["date_of_birth"]["value"],
            "gender": fields["gender"]["value"],
            "nationality": fields["nationality"]["value"],
            "place_of_origin": fields["place_of_origin"]["value"],
            "place_of_residence": fields["place_of_residence"]["value"],
            "date_of_expiry": fields["date_of_expiry"]["value"],
            "date_of_issue": fields["date_of_issue"]["value"],
            "issuing_authority": fields["issuing_authority"]["value"],
            "identifying_features": fields["identifying_features"]["value"],
            "mrz_code": fields["mrz_code"]["value"],
            "confidence_score": merged["overall_confidence"],
            "processing_time_sec": total_time,
            "image_front_path": f_url,
            "image_back_path": b_url,
            "raw_detection_json": {"front_boxes": f_boxes, "back_boxes": b_boxes},
        }
        save_record(db_payload)

        field_details = {
            k: FieldDetail(value=v["value"], confidence=round(v["confidence"], 2))
            for k, v in fields.items()
        }

        return OCRScanResponse(
            id=record_id,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            document_type=merged["document_type"],
            side="BOTH",
            overall_confidence=merged["overall_confidence"],
            processing_time_sec=total_time,
            fields=field_details,
            warnings=merged["warnings"],
            image_url=f_url,
            image_back_url=b_url,
            detected_boxes=[
                BoundingBox(box=b["box"], text=b["text"], confidence=round(b["confidence"], 2))
                for b in f_boxes
            ]
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi ghép 2 mặt webcam: {str(e)}")

@router.post("/scan-both", response_model=OCRScanResponse, summary="Quét cả 2 mặt trước và sau (Ghép thông tin)")
async def scan_both_sides(
    request: Request,
    front_file: Optional[UploadFile] = File(None, description="Ảnh mặt trước CCCD/CMND"),
    back_file: Optional[UploadFile] = File(None, description="Ảnh mặt sau CCCD/CMND")
):
    """
    Tải lên đồng thời cả 2 mặt trước và sau, ghép toàn bộ thông tin
    thành 1 hồ sơ CCCD hoàn chỉnh (Số, Họ tên, Ngày sinh, Quê quán, Ngày cấp, Nơi cấp, v.v.).
    Hỗ trợ linh hoạt cả Multipart Form lẫn JSON Base64.
    """
    try:
        t0 = time.time()
        front_bytes = None
        back_bytes = None

        # 1. Thử lấy từ tham số UploadFile
        if front_file is not None:
            try: front_bytes = await front_file.read()
            except Exception: pass
        if back_file is not None:
            try: back_bytes = await back_file.read()
            except Exception: pass

        # 2. Nếu thiếu dữ liệu, giải mã qua Request linh hoạt (Multipart hoặc JSON)
        if not front_bytes or not back_bytes:
            content_type = request.headers.get("content-type", "").lower()
            if "application/json" in content_type:
                try:
                    body = await request.json()
                    import base64 as b64
                    f_b64 = body.get("front_base64") or body.get("front_file") or body.get("front") or ""
                    b_b64 = body.get("back_base64") or body.get("back_file") or body.get("back") or ""
                    if "," in f_b64: f_b64 = f_b64.split(",", 1)[-1]
                    if "," in b_b64: b_b64 = b_b64.split(",", 1)[-1]
                    if f_b64: front_bytes = b64.b64decode(f_b64)
                    if b_b64: back_bytes = b64.b64decode(b_b64)
                except Exception as json_e:
                    print(f"[SCAN-BOTH] JSON decode error: {json_e}")
            else:
                try:
                    form = await request.form()
                    f_item = form.get("front_file") or form.get("file_front") or form.get("front")
                    b_item = form.get("back_file") or form.get("file_back") or form.get("back")

                    if f_item is not None:
                        if hasattr(f_item, "read"): front_bytes = await f_item.read()
                        elif isinstance(f_item, (bytes, bytearray)): front_bytes = bytes(f_item)
                        elif isinstance(f_item, str) and f_item.startswith("data:image"):
                            import base64 as b64
                            front_bytes = b64.b64decode(f_item.split(",", 1)[-1])

                    if b_item is not None:
                        if hasattr(b_item, "read"): back_bytes = await b_item.read()
                        elif isinstance(b_item, (bytes, bytearray)): back_bytes = bytes(b_item)
                        elif isinstance(b_item, str) and b_item.startswith("data:image"):
                            import base64 as b64
                            back_bytes = b64.b64decode(b_item.split(",", 1)[-1])
                except Exception as form_e:
                    print(f"[SCAN-BOTH] Form parse error: {form_e}")

        if not front_bytes or not back_bytes:
            raise HTTPException(
                status_code=400,
                detail="Vui lòng chọn đầy đủ cả 2 ảnh Mặt Trước và Mặt Sau."
            )

        # Process front & back in threadpool
        f_id, f_extracted, f_boxes, _, f_url = await run_in_threadpool(
            process_single_image, front_bytes, "front", side_hint="FRONT"
        )
        b_id, b_extracted, b_boxes, _, b_url = await run_in_threadpool(
            process_single_image, back_bytes, "back", side_hint="BACK"
        )

        merged = merge_front_and_back(f_extracted, b_extracted)
        total_time = round(time.time() - t0, 2)

        record_id = str(uuid.uuid4())
        fields = merged["fields"]

        db_payload = {
            "id": record_id,
            "document_type": merged["document_type"],
            "side": "BOTH",
            "id_number": fields["id_number"]["value"],
            "full_name": fields["full_name"]["value"],
            "date_of_birth": fields["date_of_birth"]["value"],
            "gender": fields["gender"]["value"],
            "nationality": fields["nationality"]["value"],
            "place_of_origin": fields["place_of_origin"]["value"],
            "place_of_residence": fields["place_of_residence"]["value"],
            "date_of_expiry": fields["date_of_expiry"]["value"],
            "date_of_issue": fields["date_of_issue"]["value"],
            "issuing_authority": fields["issuing_authority"]["value"],
            "identifying_features": fields["identifying_features"]["value"],
            "mrz_code": fields["mrz_code"]["value"],
            "confidence_score": merged["overall_confidence"],
            "processing_time_sec": total_time,
            "image_front_path": f_url,
            "image_back_path": b_url,
            "raw_detection_json": {"front_boxes": f_boxes, "back_boxes": b_boxes},
        }
        save_record(db_payload)

        field_details = {
            k: FieldDetail(value=v["value"], confidence=round(v["confidence"], 2))
            for k, v in fields.items()
        }

        return OCRScanResponse(
            id=record_id,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            document_type=merged["document_type"],
            side="BOTH",
            overall_confidence=merged["overall_confidence"],
            processing_time_sec=total_time,
            fields=field_details,
            warnings=merged["warnings"],
            image_url=f_url,
            image_back_url=b_url,
            detected_boxes=[
                BoundingBox(box=b["box"], text=b["text"], confidence=round(b["confidence"], 2))
                for b in f_boxes
            ]
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi ghép 2 mặt thẻ: {str(e)}")
