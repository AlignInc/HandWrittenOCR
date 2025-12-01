import json
import logging
from sqlalchemy.orm import Session
from models import Batch, Image, OcrResult, BatchStatus
from database import SessionLocal
from ocr.processor import get_processor

logger = logging.getLogger(__name__)

def process_batch(batch_id: str):
    """
    Process all images in a batch with OCR
    This runs as an async RQ job
    """
    db = SessionLocal()
    
    try:
        # Get batch
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            logger.error(f"Batch {batch_id} not found")
            return
        
        # Update status to processing
        batch.status = BatchStatus.PROCESSING
        db.commit()
        
        logger.info(f"Processing batch {batch_id} with {len(batch.images)} images")
        
        # Get OCR processor
        processor = get_processor()

        success_count = 0
        failures = []
        
        # Process each image
        for image in batch.images:
            try:
                logger.info(f"Processing image {image.id}: {image.file_path}")
                
                # Run OCR end-to-end (returns dict with data/confidence/raw_text)
                result = processor.process_document(
                    image.file_path,
                    batch.form_type
                )

                if not result or not result.get("raw_text"):
                    raise ValueError("OCR returned empty result")
                
                # Save OCR result
                ocr_result = OcrResult(
                    image_id=image.id,
                    data_json=json.dumps(result.get("data", {}), ensure_ascii=False),
                    confidence_json=json.dumps(result.get("confidence", {}), ensure_ascii=False),
                    raw_text=result.get("raw_text", "")
                )
                db.add(ocr_result)
                db.commit()
                
                logger.info(f"Successfully processed image {image.id}")
                success_count += 1
                
            except Exception as e:
                logger.exception(f"Error processing image {image.id}: {e}")
                failures.append(f"Image {image.page_index}: {e}")
                # Continue with next image even if one fails
                continue
        
        if success_count == 0:
            batch.status = BatchStatus.ERROR
            batch.error_message = "; ".join(failures) if failures else "OCR produced no results"
            logger.error("Batch %s failed: %s", batch_id, batch.error_message)
        else:
            batch.status = BatchStatus.DONE
            if failures:
                batch.error_message = "; ".join(failures)
                logger.warning("Batch %s completed with partial failures: %s", batch_id, batch.error_message)
            logger.info(f"Batch {batch_id} processing complete ({success_count} succeeded, {len(failures)} failed)")

        db.commit()
        
    except Exception as e:
        logger.exception(f"Error processing batch {batch_id}: {e}")
        
        # Update batch status to error
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if batch:
            batch.status = BatchStatus.ERROR
            batch.error_message = str(e)
            db.commit()
    
    finally:
        db.close()
