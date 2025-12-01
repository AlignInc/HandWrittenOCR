from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime
from models import BatchStatus

class ImageResponse(BaseModel):
    id: str
    page_index: int
    file_path: str
    ocr_data: Optional[Dict[str, Any]] = None
    confidence: Optional[Dict[str, float]] = None
    raw_text: Optional[str] = None
    
    class Config:
        from_attributes = True

class BatchResponse(BaseModel):
    id: str
    status: BatchStatus
    form_type: str
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    images: List[ImageResponse] = []
    
    class Config:
        from_attributes = True

class BatchCreate(BaseModel):
    form_type: str = "GCCF_10K"

class BatchUpdate(BaseModel):
    data: Dict[str, Any]  # Updated field values
    
class ExportFormat(str):
    CSV = "csv"
    MARKDOWN = "md"
