import os
import uuid
import logging
from typing import Optional
from datetime import datetime, timezone

from app.core.config import settings
from app.engine.models import DocumentRepresentation, PageRepresentation
from app.engine.preprocessing import preprocess_for_pipeline
from app.engine.ocr import extract_ocr_data
from app.engine.layout import analyze_layout
import cv2

logger = logging.getLogger(__name__)


def process_document(file_path: str, document_id: Optional[str] = None, status_callback=None) -> DocumentRepresentation:
    """
    Core Document Intelligence pipeline orchestration.
    1. Preprocesses the file (validation, rendering, deskew, noise reduction, contrast).
    2. Runs layout analysis (headers, footers, tables, barcodes).
    3. Runs OCR (text, bounding boxes).
    4. Aggregates and returns a DocumentRepresentation.
    """
    if not document_id:
        document_id = str(uuid.uuid4())
        
    logger.info(f"Starting Document Intelligence Pipeline for doc_id: {document_id}")
    
    # Prepare an output directory for intermediate rendered images
    output_dir = os.path.join(settings.UPLOAD_DIR, "v2_processed", str(document_id))
    
    try:
        # Step 1: Preprocessing
        if status_callback:
            status_callback("preprocessing")
        logger.info(f"[{document_id}] Running preprocessing...")
        page_image_paths = preprocess_for_pipeline(file_path, output_dir)
        
        pages = []
        for idx, img_path in enumerate(page_image_paths):
            logger.info(f"[{document_id}] Processing page {idx + 1}/{len(page_image_paths)}...")
            
            # Read image dimensions
            img = cv2.imread(img_path)
            h, w = 0, 0
            if img is not None:
                h, w = img.shape[:2]
                
            # Step 2: OCR
            if status_callback:
                status_callback("ocr_processing")
            logger.info(f"[{document_id}] Running OCR extraction...")
            ocr_words = extract_ocr_data(img_path)
            
            # Step 3: Layout Analysis
            logger.info(f"[{document_id}] Running layout analysis...")
            regions = analyze_layout(img_path, ocr_words)
            
            # Build PageRepresentation
            page_rep = PageRepresentation(
                page_number=idx + 1,
                image_path=img_path,
                original_width=w,
                original_height=h,
                words=ocr_words,
                regions=regions
            )
            pages.append(page_rep)
            
        doc_rep = DocumentRepresentation(
            document_id=str(document_id),
            pages=pages,
            metadata={
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "file_path": file_path,
                "pipeline_version": "v2"
            }
        )
        
        logger.info(f"[{document_id}] Document Intelligence Pipeline completed successfully.")
        return doc_rep
        
    except Exception as e:
        logger.error(f"[{document_id}] Pipeline failed: {e}", exc_info=True)
        raise
