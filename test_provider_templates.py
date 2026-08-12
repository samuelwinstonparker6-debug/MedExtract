import cv2
import numpy as np
import os
import time
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.domain import Document, ProviderReference
from app.services.template_extractor import generate_fingerprint
from app.services.fraud_detection import check_document_for_fraud

def create_image(filename, lines):
    img = np.ones((800, 800, 3), dtype=np.uint8) * 255
    font = cv2.FONT_HERSHEY_SIMPLEX
    y = 100
    for line in lines:
        cv2.putText(img, line, (50, y), font, 0.8, (0, 0, 0), 1)
        y += 50
    cv2.imwrite(filename, img)
    return filename

def run_test():
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    
    # 1. Create reference image
    ref_file = create_image("ref_sunrise.png", [
        "Sunrise Health Medical Center",
        "Medical Invoice",
        "License: 1234",
        "Patient: Bob",
        "Date: 2026-08-01",
        "Total Amount Due: $350.00"
    ])
    
    # Generate fingerprint and register
    fp = generate_fingerprint(ref_file)
    ref = ProviderReference(
        category="hospital",
        label="Sunrise Base",
        fingerprint_data=fp
    )
    db.add(ref)
    db.commit()
    print("Registered reference template:", ref.label)
    
    # 2. Create genuine-style doc
    gen_file = create_image("gen_sunrise.png", [
        "Sunrise Health Medical Center",
        "Medical Invoice",
        "License: 1234",
        "Patient: Alice", # different patient, same layout
        "Date: 2026-08-05",
        "Total Amount Due: $150.00"
    ])
    gen_fp = generate_fingerprint(gen_file)
    gen_doc = Document(file_path=gen_file, source_type="hospital", layout_features=gen_fp)
    db.add(gen_doc)
    db.commit()
    db.refresh(gen_doc)
    
    status, score, flags = check_document_for_fraud(db, gen_doc.id)
    print(f"\n[Genuine Document Test] Verification Result: {gen_doc.reference_verification_result}")
    assert "Sunrise Base" in gen_doc.reference_verification_result, "Genuine doc failed to match!"
    
    # 3. Create completely different layout doc
    diff_file = create_image("diff_sunrise.png", [
        "   ",
        "   ",
        "   ",
        "   ",
        "SUNRISE CLINIC - TOTAL: $500",
        "Patient: Charlie",
        "Date: 2026-08-05"
    ])
    diff_fp = generate_fingerprint(diff_file)
    diff_doc = Document(file_path=diff_file, source_type="hospital", layout_features=diff_fp)
    db.add(diff_doc)
    db.commit()
    db.refresh(diff_doc)
    
    status, score, flags = check_document_for_fraud(db, diff_doc.id)
    print(f"\n[Different Layout Test] Verification Result: {diff_doc.reference_verification_result}")
    assert "Unverified Template" in diff_doc.reference_verification_result or "Template Mismatch" in diff_doc.reference_verification_result, "Different layout didn't get flagged!"
    
    print("\nAll provider template tests passed successfully!")
    db.close()

if __name__ == "__main__":
    run_test()
