import logging
import time
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models.domain import Document
from app.core.database import SessionLocal
from app.engine.preprocessing import preprocess_for_embedding
from app.engine.layout import generate_structural_embedding
from app.engine.extraction import extract_structured_data
from app.services.fraud_service import check_document_for_fraud
from app.api.license_keys import verify_license_key

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def process_document_pipeline(document_id: int):
    """
    Version 2 Background task to process a document.
    Replaces old OCR-heavy pipeline with the new AI Engine pipeline.
    """
    db: Session = SessionLocal()
    document = None
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.error(f"Document {document_id} not found.")
            return

        file_path = document.file_path
        logger.info(f"Processing document {document_id} using V2 pipeline")
        t_total_start = time.time()

        from app.engine.pipeline import process_document
        from app.engine.fingerprint import generate_template_fingerprint
        from app.engine.similarity import get_similarity_engine

        def set_status(new_status: str):
            document.status = new_status
            db.commit()

        # 1 & 2 & 3. Preprocessing, Layout, OCR via V2 Pipeline
        doc_rep = process_document(file_path, str(document.id), status_callback=set_status)

        # Extract plain text from OCR output
        all_text = []
        for page in doc_rep.pages:
            for word in page.words:
                all_text.append(word.text)
        document.extracted_text = " ".join(all_text)
        
        # Perform heuristic extraction
        document.structured_data = extract_structured_data(
            document.extracted_text, 
            doc_rep.pages[0].image_path
        )

        # License verification based on extracted structured data
        license_number = None
        patient_name = None
        license_verification_note = None
        if document.structured_data:
            license_field = document.structured_data.get('license_number')
            patient_field = document.structured_data.get('patient_name')
            if isinstance(license_field, dict):
                license_number = license_field.get('value')
            if isinstance(patient_field, dict):
                patient_name = patient_field.get('value')

        if license_number and patient_name:
            verify_result = verify_license_key(db, license_number, patient_name)
            if verify_result.get('status') == 'REAL':
                license_verification_note = f"License verification: 90% confidence ({verify_result.get('reason')})"
            else:
                license_verification_note = f"License verification: Forge detected ({verify_result.get('reason')})"

            document.reference_verification_result = (
                (document.reference_verification_result or '').strip() +
                (" | " if document.reference_verification_result else '') +
                license_verification_note
            )

        # ---------------- FINGERPRINTING ---------------- #
        set_status("fingerprinting")
        # Generate structural fingerprint
        fingerprint = generate_template_fingerprint(doc_rep)
        
        set_status("extracted")
        
        # ---------------- ADVANCED PATH ---------------- #
        
        set_status("similarity_search")
        # Generate vectors and add to similarity index
        sim_engine = get_similarity_engine()
        combined_vector = sim_engine.generate_combined_vector(fingerprint, doc_rep.pages[0].image_path)
        sim_engine.add_document_to_index(str(document.id), combined_vector)
        
        document.structural_embedding = str(combined_vector[0].tolist())
        db.commit()

        # 4. Fraud detection
        t_fraud = time.time()
        logger.info(f"Running fraud detection for document {document_id}...")
        fraud_status, fraud_score, fraud_flags = check_document_for_fraud(db, document.id)
        
        document.status = "completed"
        document.fraud_status = fraud_status
        document.fraud_score = fraud_score
        document.fraud_flags = fraud_flags
        document.completed_timestamp = func.now()
        db.commit()

        # 5. Cleanup temporary processed images
        import shutil
        import os
        from app.core.config import settings
        output_dir = os.path.join(settings.UPLOAD_DIR, "v2_processed", str(document.id))
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir, ignore_errors=True)

        logger.info(
            f"[TIMING] Total V2 pipeline for document {document_id}: "
            f"{time.time() - t_total_start:.2f}s  |  Fraud: {fraud_status}"
        )

    except Exception as e:
        db.rollback()
        if document:
            document.status = "failed"
            db.commit()
        logger.error(f"V2 Pipeline failed for document {document_id}: {str(e)}", exc_info=True)
    finally:
        db.close()
