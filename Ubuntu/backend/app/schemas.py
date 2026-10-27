from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class FieldDetail(BaseModel):
    value: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

class ExtractedCardFields(BaseModel):
    # Front side fields
    id_number: FieldDetail = Field(default_factory=FieldDetail)
    full_name: FieldDetail = Field(default_factory=FieldDetail)
    date_of_birth: FieldDetail = Field(default_factory=FieldDetail)
    gender: FieldDetail = Field(default_factory=FieldDetail)
    nationality: FieldDetail = Field(default_factory=FieldDetail)
    place_of_origin: FieldDetail = Field(default_factory=FieldDetail)
    place_of_residence: FieldDetail = Field(default_factory=FieldDetail)
    date_of_expiry: FieldDetail = Field(default_factory=FieldDetail)
    
    # Back side fields
    date_of_issue: FieldDetail = Field(default_factory=FieldDetail)
    issuing_authority: FieldDetail = Field(default_factory=FieldDetail)
    identifying_features: FieldDetail = Field(default_factory=FieldDetail)
    mrz_code: FieldDetail = Field(default_factory=FieldDetail)

class BoundingBox(BaseModel):
    box: List[List[float]]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    text: str
    confidence: float

class OCRScanResponse(BaseModel):
    id: str
    created_at: str
    document_type: str  # CCCD_CHIP, CCCD_BARCODE, CMND_12, CMND_9, UNKNOWN
    side: str           # FRONT, BACK, BOTH
    overall_confidence: float
    processing_time_sec: float
    fields: Dict[str, FieldDetail]
    warnings: List[str] = []
    image_url: Optional[str] = None
    image_back_url: Optional[str] = None
    detected_boxes: Optional[List[BoundingBox]] = None
    raw_texts: Optional[List[str]] = None

class WebcamScanRequest(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded image string (with or without data URL prefix)")
    side_hint: Optional[str] = Field(default="auto", description="front | back | auto")
    document_type_hint: Optional[str] = Field(default="auto", description="cccd | cmnd | auto")

class WebcamBothScanRequest(BaseModel):
    front_base64: str = Field(..., description="Base64 encoded front card image (with or without data URL prefix)")
    back_base64: str = Field(..., description="Base64 encoded back card image (with or without data URL prefix)")

class RecordUpdatePayload(BaseModel):
    id_number: Optional[str] = None
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    place_of_origin: Optional[str] = None
    place_of_residence: Optional[str] = None
    date_of_expiry: Optional[str] = None
    date_of_issue: Optional[str] = None
    issuing_authority: Optional[str] = None
    identifying_features: Optional[str] = None
    document_type: Optional[str] = None
    is_verified: Optional[int] = None
    notes: Optional[str] = None

class HistoryListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[Dict[str, Any]]

class StatsResponse(BaseModel):
    total_scans: int
    today_scans: int
    average_confidence: float
    average_processing_time_sec: float
    distribution_by_type: Dict[str, int]
    recent_daily_trends: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    ocr_engine: str
    gpu_enabled: bool
