import io
import csv
import pandas as pd
from typing import List, Dict, Any

def export_records_to_csv(records: List[Dict[str, Any]]) -> bytes:
    """Exports OCR records to CSV bytes with UTF-8-SIG (BOM for Excel).
    Includes full extracted information and precise human-edit audit trail.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Detailed Header
    headers = [
        "Mã hồ sơ",
        "Thời gian quét",
        "Loại giấy tờ",
        "Mặt thẻ",
        "Số CCCD/CMND",
        "Họ và tên",
        "Ngày sinh",
        "Giới tính",
        "Quốc tịch",
        "Quê quán",
        "Nơi thường trú",
        "Có giá trị đến",
        "Ngày cấp",
        "Nơi cấp",
        "Đặc điểm nhận dạng",
        "Mã MRZ",
        "Độ tin cậy OCR (%)",
        "Thời gian xử lý (giây)",
        "Trạng thái kiểm duyệt",
        "Người dùng đã sửa",
        "Danh sách trường đã sửa",
        "Chi tiết các trường đã sửa (Trước ➔ Sau)",
        "Ghi chú"
    ]
    writer.writerow(headers)

    for r in records:
        conf_pct = round((r.get("confidence_score") or 0.0) * 100, 1)
        proc_time = round(r.get("processing_time_sec") or 0.0, 2)
        is_verified = "Đã xác nhận" if r.get("is_verified") else "Chưa duyệt"
        
        edited_fields = r.get("edited_fields") or ""
        edit_history = r.get("edit_history") or ""
        
        has_user_edited = "Có" if (edited_fields and edited_fields != "Giữ nguyên kết quả quét gốc") else "Không"
        display_edited_fields = edited_fields if edited_fields else "Giữ nguyên kết quả quét gốc"
        display_edit_history = edit_history if edit_history else "Không chỉnh sửa"

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
            r.get("mrz_code") or "",
            conf_pct,
            proc_time,
            is_verified,
            has_user_edited,
            display_edited_fields,
            display_edit_history,
            r.get("notes") or ""
        ])

    # Prepend UTF-8 BOM so Excel opens it with proper Vietnamese accents
    return "\ufeff".encode("utf-8") + output.getvalue().encode("utf-8")

def export_records_to_excel(records: List[Dict[str, Any]]) -> bytes:
    """Exports OCR records to Excel (.xlsx) file bytes with formatted audit columns."""
    rows = []
    for r in records:
        edited_fields = r.get("edited_fields") or ""
        edit_history = r.get("edit_history") or ""
        has_user_edited = "Có" if (edited_fields and edited_fields != "Giữ nguyên kết quả quét gốc") else "Không"
        display_edited_fields = edited_fields if edited_fields else "Giữ nguyên kết quả quét gốc"
        display_edit_history = edit_history if edit_history else "Không chỉnh sửa"

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
            "Mã MRZ": r.get("mrz_code") or "",
            "Độ tin cậy OCR (%)": round((r.get("confidence_score") or 0.0) * 100, 1),
            "Thời gian xử lý (giây)": round(r.get("processing_time_sec") or 0.0, 2),
            "Trạng thái kiểm duyệt": "Đã xác nhận" if r.get("is_verified") else "Chưa duyệt",
            "Người dùng đã sửa": has_user_edited,
            "Danh sách trường đã sửa": display_edited_fields,
            "Chi tiết các trường đã sửa (Trước ➔ Sau)": display_edit_history,
            "Ghi chú": r.get("notes") or ""
        })

    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Lich_Su_OCR_CCCD")
    output.seek(0)
    return output.getvalue()
