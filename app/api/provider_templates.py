from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import ProviderReference
import os
import shutil

router = APIRouter()

@router.get("")
def get_provider_templates(db: Session = Depends(get_db)):
    references = db.query(ProviderReference).order_by(ProviderReference.date_registered.desc()).all()
    # Group by category
    result = {
        "hospital": [],
        "doctor": [],
        "lab": []
    }
    for ref in references:
        if ref.category in result:
            result[ref.category].append({
                "id": ref.id,
                "label": ref.label,
                "date_registered": ref.date_registered
            })
    return result

@router.post("/upload")
def upload_provider_template(
    file: UploadFile = File(...),
    category: str = Form(..., description="hospital, doctor, lab"),
    label: str = Form(..., description="Label for this template"),
    db: Session = Depends(get_db)
):
    valid_categories = ["hospital", "doctor", "lab"]
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of {valid_categories}")

    from app.core.config import settings
    if file.content_type not in settings.ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{file.content_type}'")
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds maximum allowed size")

    # Temporarily save the file to generate fingerprint
    from werkzeug.utils import secure_filename
    temp_dir = "app/uploads/temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    safe_name = secure_filename(file.filename or "upload.tmp")
    if not safe_name: safe_name = "upload.tmp"
        
    temp_path = os.path.join(temp_dir, safe_name)
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        from app.engine.pipeline import process_document
        from app.engine.template_fingerprint import generate_fingerprint
        import uuid
        
        # We need a stable DocumentRepresentation, which runs preprocessing, OCR, and layout
        temp_doc_id = str(uuid.uuid4())
        doc_rep = process_document(temp_path, temp_doc_id)
        fingerprint_obj = generate_fingerprint(doc_rep)
        fingerprint_dict = fingerprint_obj.model_dump()
        
        # Serialize fingerprint dict to string to store in DB
        import json
        fingerprint = json.dumps(fingerprint_dict)
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Failed to generate fingerprint: {str(e)}")
        
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    new_ref = ProviderReference(
        category=category,
        label=label,
        fingerprint_data=fingerprint
    )
    db.add(new_ref)
    db.commit()
    db.refresh(new_ref)
    
    return {
        "message": "Template reference added successfully",
        "id": new_ref.id,
        "label": new_ref.label,
        "category": new_ref.category
    }
