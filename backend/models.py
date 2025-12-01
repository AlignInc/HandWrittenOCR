from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Text, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from database import Base

class BatchStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"

class Batch(Base):
    __tablename__ = "batches"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Enum(BatchStatus), default=BatchStatus.PENDING)
    form_type = Column(String, default="GCCF_10K")  # Form template type
    error_message = Column(Text, nullable=True)
    
    # Relationships
    images = relationship("Image", back_populates="batch", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Batch {self.id} - {self.status}>"

class Image(Base):
    __tablename__ = "images"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String, ForeignKey("batches.id"), nullable=False)
    file_path = Column(String, nullable=False)
    page_index = Column(Integer, default=0)  # For multi-page forms
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    batch = relationship("Batch", back_populates="images")
    ocr_result = relationship("OcrResult", back_populates="image", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Image {self.id} - Page {self.page_index}>"

class OcrResult(Base):
    __tablename__ = "ocr_results"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    image_id = Column(String, ForeignKey("images.id"), nullable=False)
    data_json = Column(Text, nullable=False)  # JSON string of extracted fields
    confidence_json = Column(Text, nullable=True)  # JSON string of confidence scores
    raw_text = Column(Text, nullable=True)  # Raw OCR output
    processed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    image = relationship("Image", back_populates="ocr_result")
    
    def __repr__(self):
        return f"<OcrResult {self.id}>"
