import time
import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from starlette.concurrency import run_in_threadpool
from ..config import STORAGE_DIR, SAMPLE_DATA_DIR, TARGET_IMAGE_WIDTH
from ..schemas import OCRScanResponse, WebcamScanRequest, BoundingBox, FieldDetail
from ..services.preprocessor import (
    read_image_from_bytes,
    read_image_from_base64,
    read_image_from_path,
    auto_orient_card,
    resize_for_ocr,
    enhance_image,
    save_image_to_storage
)
from ..services.ocr_engine import get_ocr_engine
from ..services.extractor import extract_fields, merge_front_and_back
from ..database import save_record

router = APIRouter(prefix="/api/v1/ocr", tags=["OCR Processing"])

def process_single_image(image_bytes: bytes, filename_prefix: str = "scan", side_hint: str = "auto") -> tuple:
    """Core helper to process an image array, run OCR and extract fields."""
    start_time = time.time()
    
    # 1. Read, auto-orient & enhance image
    image = read_image_from_bytes(image_bytes)
    image, _ = auto_orient_card(image)
    resized, scale = resize_for_ocr(image, target_width=TARGET_IMAGE_WIDTH)
    enhanced = enhance_image(resized)

    # 2. Run OCR
    engine = get_ocr_engine()
    raw_boxes = engine.run_ocr(enhanced)

    # 3. Extract Fields
    extracted = extract_fields(raw_boxes, side_hint=side_hint)
    elapsed = round(time.time() - start_time, 2)

    # 4. Save image to storage safely
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
    image, _ = auto_orient_card(image)
    resized, scale = resize_for_ocr(image, target_width=TARGET_IMAGE_WIDTH)
    enhanced = enhance_image(resized)

    engine = get_ocr_engine()
    raw_boxes = engine.run_ocr(enhanced)
    extracted = extract_fields(raw_boxes, side_hint=side_hint)
    elapsed = round(time.time() - start_time, 2)

    record_id = str(uuid.uuid4())
    img_name = f"webcam_{record_id}.jpg"
    img_path = STORAGE_DIR / img_name
    saved_path = save_image_to_storage(image, img_path)
    img_url = f"/storage/{img_name}" if saved_path else None

    return record_id, extracted, raw_boxes, elapsed, img_url

def process_sample_image(front_img_path: Path, target_folder_name: str) -> tuple:
    """Core helper to load a sample card image from disk, run OCR and extract fields."""
    t0 = time.time()
    image = read_image_from_path(front_img_path)
    image, _ = auto_orient_card(image)
    resized, scale = resize_for_ocr(image, target_width=TARGET_IMAGE_WIDTH)
    enhanced = enhance_image(resized)

    engine = get_ocr_engine()
    raw_boxes = engine.run_ocr(enhanced)
    extracted = extract_fields(raw_boxes, side_hint="FRONT")
    elapsed = round(time.time() - t0, 2)

    record_id = str(uuid.uuid4())
    img_name = f"sample_{target_folder_name}_{record_id}.jpg"
    saved_path = save_image_to_storage(image, STORAGE_DIR / img_name)
    img_url = f"/storage/{img_name}" if saved_path else None

    return record_id, extracted, raw_boxes, elapsed, img_url

@router.post("/scan", response_model=OCRScanResponse, summary="Quét ảnh CCCD/CMND tải lên (File upload)")
async def scan_file(
    file: UploadFile = File(..., description="File ảnh thẻ CCCD/CMND (JPG, PNG, JPEG)"),
    side_hint: Optional[str] = Form("auto", description="Gợi ý mặt thẻ: front | back | auto")
):
    """
    Nhận diện kí tự và trích xuất thông tin từ file ảnh tải lên.
    Tự động phân loại mặt trước/sau và loại thẻ nếu để side_hint='auto'.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Vui lòng tải lên file định dạng hình ảnh hợp lệ.")

    try:
        content = await file.read()
        record_id, extracted, raw_boxes, elapsed, img_url = await run_in_threadpool(
            process_single_image, content, filename_prefix="upload", side_hint=side_hint.upper()
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
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý OCR webcam: {str(e)}")

@router.post("/scan-both", response_model=OCRScanResponse, summary="Quét cả 2 mặt trước và sau (Ghép thông tin)")
async def scan_both_sides(
    front_file: UploadFile = File(..., description="Ảnh mặt trước CCCD/CMND"),
    back_file: UploadFile = File(..., description="Ảnh mặt sau CCCD/CMND")
):
    """
    Tải lên đồng thời cả 2 mặt trước và sau, ghép toàn bộ thông tin
    thành 1 hồ sơ CCCD hoàn chỉnh (Số, Họ tên, Ngày sinh, Quê quán, Ngày cấp, Nơi cấp, v.v.).
    """
    try:
        t0 = time.time()
        front_bytes = await front_file.read()
        back_bytes = await back_file.read()

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
        raise HTTPException(status_code=500, detail=f"Lỗi ghép 2 mặt thẻ: {str(e)}")

@router.post("/demo-sample", response_model=OCRScanResponse, summary="Chạy thử với bộ dữ liệu mẫu có sẵn")
async def scan_demo_sample(
    sample_index: int = Form(0, description="Chỉ số thư mục mẫu trong Dữ liệu mẫu (0-47)")
):
    """
    Chạy thử nghiệm hệ thống trực tiếp trên tập dữ liệu mẫu trong thư mục 'Dữ liệu mẫu'.
    """
    if not SAMPLE_DATA_DIR.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy thư mục 'Dữ liệu mẫu' trong dự án.")

    subdirs = sorted([d for d in SAMPLE_DATA_DIR.iterdir() if d.is_dir()])
    if not subdirs:
        raise HTTPException(status_code=404, detail="Thư mục 'Dữ liệu mẫu' trống.")

    idx = sample_index % len(subdirs)
    target_folder = subdirs[idx]

    # Look for image files
    imgs = list(target_folder.glob("*.png")) + list(target_folder.glob("*.jpg"))
    if not imgs:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy ảnh trong {target_folder.name}")

    try:
        # Load front image (usually Tệp_000(1).png or first)
        front_img_path = target_folder / "Tệp_000(1).png"
        if not front_img_path.exists():
            front_img_path = imgs[0]

        record_id, extracted, raw_boxes, elapsed, img_url = await run_in_threadpool(
            process_sample_image, front_img_path, target_folder.name
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
            "confidence_score": extracted["overall_confidence"],
            "processing_time_sec": elapsed,
            "image_front_path": img_url,
            "raw_detection_json": raw_boxes,
            "notes": f"Mẫu kiểm thử từ {target_folder.name}"
        }
        save_record(db_payload)

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
            detected_boxes=[
                BoundingBox(box=b["box"], text=b["text"], confidence=round(b["confidence"], 2))
                for b in raw_boxes
            ],
            raw_texts=[b["text"] for b in raw_boxes]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi kiểm thử dữ liệu mẫu: {str(e)}")
