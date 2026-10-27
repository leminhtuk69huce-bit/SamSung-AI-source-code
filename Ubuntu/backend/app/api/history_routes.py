from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..database import list_records, get_record_by_id, update_record, delete_record
from ..schemas import HistoryListResponse, RecordUpdatePayload

router = APIRouter(prefix="/api/v1/ocr", tags=["History & Records"])

@router.get("/history", response_model=HistoryListResponse, summary="Lấy danh sách lịch sử scan")
async def get_history(
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên, số CCCD hoặc địa chỉ"),
    document_type: Optional[str] = Query(None, description="Lọc theo loại: CCCD_CHIP, CMND_12, CMND_9"),
    side: Optional[str] = Query(None, description="Lọc theo mặt: FRONT, BACK, BOTH"),
    limit: int = Query(20, ge=1, le=100, description="Số bản ghi mỗi trang"),
    offset: int = Query(0, ge=0, description="Vị trí bắt đầu")
):
    """
    Trả về danh sách lịch sử các lần scan OCR có hỗ trợ tìm kiếm và phân trang.
    """
    result = list_records(
        search=search,
        document_type=document_type,
        side=side,
        limit=limit,
        offset=offset
    )
    return HistoryListResponse(**result)

@router.get("/history/{record_id}", summary="Lấy chi tiết 1 hồ sơ scan")
async def get_history_detail(record_id: str):
    """
    Xem thông tin chi tiết của một lần scan bằng ID (bao gồm cả bounding boxes nhận diện).
    """
    record = get_record_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi OCR với ID này.")
    return {"status": "success", "data": record}

@router.put("/history/{record_id}", summary="Chỉnh sửa thông tin hồ sơ scan")
async def update_history_record(record_id: str, payload: RecordUpdatePayload):
    """
    Cho phép người dùng hoặc nhân viên kiểm duyệt chỉnh sửa lại các trường thông tin
    nếu OCR nhận diện sai (Human-in-the-loop verification).
    """
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="Không có dữ liệu cập nhật.")

    success = update_record(record_id, updates)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi cần cập nhật.")

    updated_record = get_record_by_id(record_id)
    return {"status": "success", "message": "Cập nhật bản ghi thành công", "data": updated_record}

@router.delete("/history/{record_id}", summary="Xóa 1 hồ sơ scan")
async def delete_history_record(record_id: str):
    """
    Xóa một bản ghi lịch sử khỏi cơ sở dữ liệu.
    """
    success = delete_record(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi để xóa.")
    return {"status": "success", "message": f"Đã xóa thành công hồ sơ {record_id}"}
