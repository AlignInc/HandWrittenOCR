from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
import json
import shutil
from pathlib import Path
from datetime import datetime
from redis import Redis
from redis.exceptions import RedisError
from rq import Queue

from database import get_db
from models import Batch, Image, OcrResult, BatchStatus
from schemas import BatchResponse, BatchUpdate, ImageResponse
from config import UPLOAD_DIR, EXPORT_DIR, REDIS_URL
import os
from workers.batch_processor import process_batch
from exporters.csv_exporter import export_single_to_csv
from exporters.markdown_exporter import export_to_markdown

router = APIRouter(prefix="/api/batches", tags=["batches"])

# Redis queue for async processing
redis_conn = Redis.from_url(REDIS_URL)
task_queue = Queue(connection=redis_conn)

@router.post("", response_model=BatchResponse, status_code=201)
async def create_batch(
    images: List[UploadFile] = File(...),
    form_type: str = Query("GCCF_10K"),
    db: Session = Depends(get_db)
):
    """
    Upload multiple images and create a new batch for OCR processing
    """
    if not images:
        raise HTTPException(status_code=400, detail="No images provided")
    
    # Create batch
    batch = Batch(form_type=form_type)
    db.add(batch)
    db.commit()
    db.refresh(batch)
    
    # Create upload directory for this batch
    batch_dir = UPLOAD_DIR / datetime.now().strftime("%Y-%m-%d") / batch.id
    batch_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded images
    for idx, upload_file in enumerate(images):
        # Generate unique filename
        file_ext = Path(upload_file.filename).suffix
        file_path = batch_dir / f"page_{idx}{file_ext}"
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        # Create image record
        image = Image(
            batch_id=batch.id,
            file_path=str(file_path),
            page_index=idx
        )
        db.add(image)
    
    db.commit()
    
    # Decide processing mode
    use_sync = os.getenv("SYNC_PROCESSING", "false").lower() == "true"
    single_image = len(images) == 1

    try:
        if use_sync or single_image:
            # Immediate processing in the API process for single uploads or when forced sync
            process_batch(batch.id)
        else:
            task_queue.enqueue(process_batch, batch.id, job_timeout='10m')
    except RedisError:
        # Redis unavailable – fall back to synchronous processing to avoid hanging spinner
        process_batch(batch.id)
    
    # Return batch info
    return _build_batch_response(batch, db)

@router.get("/{batch_id}", response_model=BatchResponse)
def get_batch(batch_id: str, db: Session = Depends(get_db)):
    """
    Get batch status and OCR results
    """
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return _build_batch_response(batch, db)

@router.put("/{batch_id}", response_model=BatchResponse)
def update_batch(
    batch_id: str,
    update: BatchUpdate,
    db: Session = Depends(get_db)
):
    """
    Update OCR results after user edits
    """
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Update OCR results for the first image (or merge all images)
    # This assumes single-form batch; for multi-page, you'd need to specify which image
    if batch.images and batch.images[0].ocr_result:
        ocr_result = batch.images[0].ocr_result
        
        # Merge user updates with existing data
        existing_data = json.loads(ocr_result.data_json) if ocr_result.data_json else {}
        existing_data.update(update.data)
        
        ocr_result.data_json = json.dumps(existing_data, ensure_ascii=False)
        db.commit()
    
    return _build_batch_response(batch, db)

@router.get("/{batch_id}/export")
def export_batch(
    batch_id: str,
    format: str = Query("csv", regex="^(csv|md)$"),
    db: Session = Depends(get_db)
):
    """
    Export batch results as CSV or Markdown
    File is saved to server directory and returned for download
    """
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    if batch.status != BatchStatus.DONE:
        raise HTTPException(status_code=400, detail="Batch processing not complete")
    
    # Collect all OCR data
    all_data = {}
    all_confidence = {}
    
    for image in batch.images:
        if image.ocr_result:
            data = json.loads(image.ocr_result.data_json) if image.ocr_result.data_json else {}
            confidence = json.loads(image.ocr_result.confidence_json) if image.ocr_result.confidence_json else {}
            all_data.update(data)
            all_confidence.update(confidence)
    
    # Create export directory
    export_date_dir = EXPORT_DIR / datetime.now().strftime("%Y-%m-%d")
    export_date_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate export content
    if format == "csv":
        content = export_single_to_csv(all_data, batch.form_type)
        filename = f"batch_{batch.id}.csv"
        media_type = "text/csv"
    else:  # markdown
        content = export_to_markdown(all_data, batch.form_type, all_confidence)
        filename = f"batch_{batch.id}.md"
        media_type = "text/markdown"
    
    # Save to server directory
    export_path = export_date_dir / filename
    with open(export_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    # Return as download
    return Response(
        content=content.encode("utf-8"),
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

def _build_batch_response(batch: Batch, db: Session) -> BatchResponse:
    """Build batch response with OCR results"""
    images_data = []
    
    for image in batch.images:
        image_data = ImageResponse(
            id=image.id,
            page_index=image.page_index,
            file_path=image.file_path
        )
        
        if image.ocr_result:
            image_data.ocr_data = json.loads(image.ocr_result.data_json) if image.ocr_result.data_json else {}
            image_data.confidence = json.loads(image.ocr_result.confidence_json) if image.ocr_result.confidence_json else {}
            image_data.raw_text = image.ocr_result.raw_text
        
        images_data.append(image_data)
    
    return BatchResponse(
        id=batch.id,
        status=batch.status,
        form_type=batch.form_type,
        created_at=batch.created_at,
        updated_at=batch.updated_at,
        error_message=batch.error_message,
        images=images_data
    )
