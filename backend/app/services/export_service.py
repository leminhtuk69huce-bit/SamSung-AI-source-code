import io
import csv
import pandas as pd
from typing import List, Dict, Any

def export_records_to_csv(records: List[Dict[str, Any]]) -> bytes:
    """Exports OCR records to CSV bytes with UTF-8-SIG (BOM for Excel)."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    headers = [
        "Mã hồ sơ", "Thời gian quét", "Loại giấy tờ", "Mặt", "Số CCCD/CMND",
        "Họ và tên", "Ngày sinh", "Giới tính", "Quốc tịch", "Quê quán",
        "Nơi thường trú", "Có giá trị đến", "Ngày cấp", "Nơi cấp",
        "Đặc điểm nhận dạng", "Độ tin cậy", "Thời gian xử lý (s)", "Đã xác thực", "Ghi chú"
    ]
    writer.writerow(headers)

    for r in records:
        writer.writerow([
            r.get("id"),
            r.get("created_at"),
            r.get("document_type"),
            r.get("side"),
            r.get("id_number") or "",
            r.get("full_name") or "",
            r.get("date_of_birth") or "",
            r.get("gender") or "",
            r.get("nationality") or "",
            r.get("place_of_origin") or "",
            r.get("place_of_residence") or "",
            r.get("date_of_expiry") or "",
            r.get("date_of_issue") or "",
            r.get("issuing_authority") or "",
            r.get("identifying_features") or "",
            r.get("confidence_score") or 0.0,
            r.get("processing_time_sec") or 0.0,
            "Đã duyệt" if r.get("is_verified") else "Chưa duyệt",
            r.get("notes") or ""
        ])

    # Prepend UTF-8 BOM so Excel opens it with proper Vietnamese accents
    return "\ufeff".encode("utf-8") + output.getvalue().encode("utf-8")

def export_records_to_excel(records: List[Dict[str, Any]]) -> bytes:
    """Exports OCR records to Excel (.xlsx) file bytes with formatted columns."""
    rows = []
    for r in records:
        rows.append({
            "Mã hồ sơ": r.get("id"),
            "Thời gian quét": r.get("created_at"),
            "Loại giấy tờ": r.get("document_type"),
            "Mặt thẻ": r.get("side"),
            "Số CCCD/CMND": r.get("id_number") or "",
            "Họ và tên": r.get("full_name") or "",
            "Ngày sinh": r.get("date_of_birth") or "",
            "Giới tính": r.get("gender") or "",
            "Quốc tịch": r.get("nationality") or "",
            "Quê quán": r.get("place_of_origin") or "",
            "Nơi thường trú": r.get("place_of_residence") or "",
            "Có giá trị đến": r.get("date_of_expiry") or "",
            "Ngày cấp": r.get("date_of_issue") or "",
            "Nơi cấp": r.get("issuing_authority") or "",
            "Đặc điểm nhận dạng": r.get("identifying_features") or "",
            "Độ tin cậy (%)": round((r.get("confidence_score") or 0.0) * 100, 1),
            "Thời gian xử lý (giây)": r.get("processing_time_sec") or 0.0,
            "Trạng thái": "Đã duyệt" if r.get("is_verified") else "Chưa duyệt",
            "Ghi chú": r.get("notes") or ""
        })

    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Lich_Su_OCR_CCCD")
    output.seek(0)
    return output.getvalue()
