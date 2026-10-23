from fastapi import APIRouter, Query, Response, HTTPException
from typing import Optional
from ..database import get_statistics, list_records
from ..schemas import StatsResponse, HealthResponse
from ..services.export_service import export_records_to_csv, export_records_to_excel
from ..config import API_TITLE, API_VERSION, OCR_GPU

router = APIRouter(prefix="/api/v1", tags=["Statistics & System"])

@router.get("/ocr/stats", response_model=StatsResponse, summary="Thống kê tổng quan cho Dashboard")
async def get_dashboard_stats():
    """
    Trả về các chỉ số KPI: tổng số lượt quét, số lượt quét trong ngày,
    độ tin cậy trung bình, thời gian xử lý trung bình và biểu đồ phân bố loại thẻ.
    """
    stats = get_statistics()
    return StatsResponse(**stats)

@router.get("/ocr/export", summary="Xuất danh sách hồ sơ (CSV hoặc Excel)")
async def export_data(
    format: str = Query("xlsx", pattern="^(xlsx|csv)$", description="Định dạng xuất file: 'xlsx' hoặc 'csv'"),
    search: Optional[str] = Query(None, description="Lọc theo từ khóa"),
    document_type: Optional[str] = Query(None, description="Lọc theo loại giấy tờ")
):
    """
    Xuất toàn bộ hoặc kết quả tìm kiếm lịch sử quét ra file Excel hoặc CSV (có UTF-8 BOM chuẩn tiếng Việt).
    """
    data = list_records(search=search, document_type=document_type, limit=10000, offset=0)
    records = data["items"]

    if not records:
        raise HTTPException(status_code=404, detail="Không có dữ liệu để xuất file.")

    if format == "csv":
        csv_bytes = export_records_to_csv(records)
        return Response(
            content=csv_bytes,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=danh_sach_ocr_cccd.csv"}
        )
    else:
        excel_bytes = export_records_to_excel(records)
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=danh_sach_ocr_cccd.xlsx"}
        )

@router.get("/health", response_model=HealthResponse, summary="Kiểm tra trạng thái hệ thống")
async def health_check():
    """
    Endpoint kiểm tra liveness và readiness của backend.
    """
    return HealthResponse(
        status="healthy",
        app_name=API_TITLE,
        version=API_VERSION,
        ocr_engine="EasyOCR (CRAFT + BiLSTM + CTC) with Vietnamese Post-Processor",
        gpu_enabled=OCR_GPU
    )

