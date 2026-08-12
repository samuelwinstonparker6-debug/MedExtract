import os
import shutil
import logging
import threading
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import DocumentNotFoundException, DocumentUploadException
from app.models.domain import Document
from app.models.schemas import DocumentResponse

logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


# ── Threading dispatch ────────────────────────────────────────────────────────

def _dispatch_processing(document_id: int) -> None:
    """
    Dispatch document processing to a background thread using the V2 AI pipeline.
    """
    try:
        from app.services.worker_service import process_document_pipeline
        t = threading.Thread(
            target=process_document_pipeline,
            args=(document_id,),
            daemon=True,
        )
        t.start()
        logger.info(f'Document #{document_id} dispatched to V2 background worker.')
    except Exception as thread_exc:
        logger.error(f'Thread fallback failed for doc #{document_id}: {thread_exc!r}')


# ── Helpers ───────────────────────────────────────────────────────────────────

from werkzeug.utils import secure_filename

def _validate_upload(file: UploadFile) -> None:
    """Raise DocumentUploadException if the file fails content-type or size checks."""
    if file.content_type not in settings.ALLOWED_CONTENT_TYPES:
        raise DocumentUploadException(
            f"Unsupported file type '{file.content_type}'. "
            f"Allowed: {', '.join(settings.ALLOWED_CONTENT_TYPES)}"
        )
    
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise DocumentUploadException(f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes.")

def _save_upload(file: UploadFile) -> tuple[str, str]:
    """
    Persist the uploaded file to UPLOAD_DIR.
    Returns (saved_filename, absolute_file_path).
    """
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Sanitize the filename to prevent path traversal
    safe_name = secure_filename(file.filename or "upload.tmp")
    if not safe_name:
        safe_name = "upload.tmp"
        
    file_path = os.path.join(settings.UPLOAD_DIR, safe_name)

    # Avoid overwriting — suffix with a counter if name already exists
    counter = 1
    base, ext = os.path.splitext(safe_name)
    while os.path.exists(file_path):
        safe_name = f'{base}_{counter}{ext}'
        file_path = os.path.join(settings.UPLOAD_DIR, safe_name)
        counter += 1

    with open(file_path, 'wb') as out:
        shutil.copyfileobj(file.file, out)

    return safe_name, file_path


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get('/', response_model=list[DocumentResponse])
def list_documents(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Return a paginated list of all documents."""
    docs = db.query(Document).offset(skip).limit(limit).all()
    return docs


@router.post('/upload', response_model=DocumentResponse, status_code=status.HTTP_202_ACCEPTED)
@limiter.limit('20/minute')
def upload_document(
    request: Request,
    file: UploadFile = File(...),
    source_type: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Upload a medical document for async processing.

    Returns 202 Accepted immediately; processing (OCR + fraud check) runs in background.
    Poll GET /{id} to check status.
    """
    _validate_upload(file)

    if source_type not in ('doctor', 'hospital', 'lab'):
        raise DocumentUploadException(
            "source_type must be one of: 'doctor', 'hospital', 'lab'."
        )

    saved_filename, file_path = _save_upload(file)

    import hashlib
    file_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            file_hash.update(chunk)
    file_hash_hex = file_hash.hexdigest()

    # Check for existing document with this hash
    existing_doc = db.query(Document).filter(
        Document.file_hash == file_hash_hex, 
        Document.status.in_(['extracted', 'completed'])
    ).first()

    db_doc = Document(
        filename=saved_filename,
        file_path=file_path,
        file_hash=file_hash_hex,
        source_type=source_type,
        status='pending',
    )
    
    if existing_doc:
        logger.info(f"Cache hit for file hash {file_hash_hex}. Reusing document {existing_doc.id}")
        db_doc.extracted_text = existing_doc.extracted_text
        db_doc.document_type = existing_doc.document_type
        db_doc.structured_data = existing_doc.structured_data
        db_doc.layout_features = existing_doc.layout_features

        db_doc.fraud_status = existing_doc.fraud_status
        db_doc.fraud_score = existing_doc.fraud_score
        db_doc.fraud_flags = existing_doc.fraud_flags
        db_doc.status = existing_doc.status
        db_doc.completed_timestamp = datetime.now(timezone.utc) if existing_doc.status == 'completed' else None
        
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        # Skip background processing entirely
        return db_doc

    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    _dispatch_processing(db_doc.id)

    return db_doc


@router.get('/fraud/alerts', response_model=list[DocumentResponse])
def get_fraud_alerts(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Return documents flagged with AMBER or RED fraud status.
    Optionally filter by a specific fraud_status value.
    """
    query = db.query(Document).filter(Document.fraud_status.in_(['AMBER', 'RED']))
    if status_filter:
        query = query.filter(Document.fraud_status == status_filter.upper())
    return query.order_by(Document.upload_timestamp.desc()).all()


@router.delete('/{document_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document and its uploaded file from the system."""
    doc = db.get(Document, document_id)
    if not doc:
        raise DocumentNotFoundException(document_id)

    try:
        if doc.file_path and os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except Exception as exc:
        logger.warning(f'Unable to delete file for document #{document_id}: {exc!r}')

    db.delete(doc)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
def delete_all_documents(db: Session = Depends(get_db)):
    """Delete all documents and remove uploaded files from disk."""
    documents = db.query(Document).all()
    for doc in documents:
        try:
            if doc.file_path and os.path.exists(doc.file_path):
                os.remove(doc.file_path)
        except Exception as exc:
            logger.warning(f'Unable to delete file for document #{doc.id}: {exc!r}')

    db.query(Document).delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/{document_id}', response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Fetch a single document by ID."""
    doc = db.get(Document, document_id)
    if not doc:
        raise DocumentNotFoundException(document_id)
    return doc


@router.get('/{document_id}/extracted')
def get_extracted_data(document_id: int, db: Session = Depends(get_db)):
    """Return the structured extracted data for a completed document."""
    doc = db.get(Document, document_id)
    if not doc:
        raise DocumentNotFoundException(document_id)
    if doc.status not in ('extracted', 'completed'):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f'Document #{document_id} has not been extracted yet (status: {doc.status}).',
        )
    return {
        'id': doc.id,
        'status': doc.status,
        'document_type': doc.document_type,
        'extracted_text': doc.extracted_text,
        'structured_data': doc.structured_data,
        'fraud_status': doc.fraud_status,
        'fraud_score': doc.fraud_score,
        'fraud_flags': doc.fraud_flags,
    }


@router.put('/{document_id}/extracted', response_model=DocumentResponse)
def update_extracted_data(
    document_id: int,
    structured_data: dict,
    db: Session = Depends(get_db),
):
    """Manually update structured data for a document (e.g., human correction)."""
    doc = db.get(Document, document_id)
    if not doc:
        raise DocumentNotFoundException(document_id)
    doc.structured_data = structured_data
    db.commit()
    db.refresh(doc)
    return doc


@router.post('/{document_id}/reprocess', response_model=DocumentResponse)
def reprocess_document(document_id: int, db: Session = Depends(get_db)):
    """
    Re-run fraud detection on an already-processed document.
    Fraud check is synchronous here (quick) — full OCR is not re-run.
    """
    doc = db.get(Document, document_id)
    if not doc:
        raise DocumentNotFoundException(document_id)

    try:
        from app.services.fraud_service import check_document_for_fraud
        fraud_status, fraud_score, fraud_flags = check_document_for_fraud(db, doc.id)
        doc.fraud_status = fraud_status
        doc.fraud_score = fraud_score
        doc.fraud_flags = fraud_flags
        doc.completed_timestamp = datetime.now(timezone.utc)
        db.commit()
        db.refresh(doc)
    except Exception as exc:
        logger.error(f'Reprocess failed for document #{document_id}: {exc!r}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Reprocess failed: {exc}',
        )

    return doc


@router.delete('/{document_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document record and its associated file from disk."""
    doc = db.get(Document, document_id)
    if not doc:
        raise DocumentNotFoundException(document_id)

    # Remove file from disk if present
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except OSError as exc:
            logger.warning(f'Could not remove file {doc.file_path}: {exc}')

    db.delete(doc)
    db.commit()


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
def delete_all_documents(db: Session = Depends(get_db)):
    """
    Delete ALL document records and their files from disk.
    Intended for development/testing only.
    """
    docs = db.query(Document).all()
    for doc in docs:
        if doc.file_path and os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except OSError as exc:
                logger.warning(f'Could not remove file {doc.file_path}: {exc}')
    db.query(Document).delete()
    db.commit()
