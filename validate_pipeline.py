import os
import json
import shutil
import sys
from sqlalchemy.orm import Session

# Ensure we can import app
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.classifier import classifier

# We have torch/transformers natively now, so we DO NOT mock get_entities.
from app.services.extractor import extract_fields



from app.core.database import SessionLocal, engine
from app.models.domain import Document, Base
from app.services.ocr import process_document_ocr

# Ensure tables exist
Base.metadata.create_all(bind=engine)

def run_validation():
    sample_dir = os.path.join("tests", "real_samples")
    expected_json_path = os.path.join(sample_dir, "expected_output.json")
    
    if not os.path.exists(expected_json_path):
        print(f"Error: {expected_json_path} not found.")
        print("Please create it and add sample documents.")
        return

    with open(expected_json_path, 'r') as f:
        expected_data = json.load(f)

    db: Session = SessionLocal()
    os.makedirs("app/uploads", exist_ok=True)

    results = []
    total_fields = 0
    matched_fields = 0
    missing_fields = 0
    mismatched_fields = 0

    print(f"\n{'Document':<30} | {'Type Match':<10} | {'Fields (Match/Mismatch/Missing)':<35}")
    print("-" * 80)

    for filename, expected in expected_data.items():
        # Ensure we test the OCR image path, not the native PDF text bypass path
        img_filename = f"sample_{filename.replace('.pdf', '.png')}"
        filepath = os.path.join(sample_dir, img_filename)
        if not os.path.exists(filepath):
            # Fallback to original if image not found
            filepath = os.path.join(sample_dir, filename)
            
        if not os.path.exists(filepath):
            print(f"{filename:<30} | {'NOT FOUND':<10} | {'-':<35}")
            continue

        # Simulate upload
        dest_path = os.path.join("app", "uploads", f"test_val_{img_filename}")
        shutil.copy(filepath, dest_path)

        doc = Document(
            source_type=expected.get("source_type", "doctor"),
            file_path=dest_path,
            status="pending"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # Run full pipeline synchronously
        process_document_ocr(doc.id)
        
        # Refresh to get extracted data
        db.refresh(doc)

        # Compare results
        exp_type = expected.get("document_type")
        exp_fields = expected.get("structured_data", {})
        
        type_match = (doc.document_type == exp_type)
        
        doc_matched = 0
        doc_mismatched = 0
        doc_missing = 0
        
        actual_fields = doc.structured_data if doc.structured_data else {}
        
        for key, exp_val in exp_fields.items():
            total_fields += 1
            act_val = actual_fields.get(key)
            if isinstance(act_val, dict) and "value" in act_val:
                act_val = act_val["value"]
            
            if act_val is None:
                doc_missing += 1
                missing_fields += 1
            elif str(act_val).strip().lower() == str(exp_val).strip().lower():
                doc_matched += 1
                matched_fields += 1
            else:
                doc_mismatched += 1
                mismatched_fields += 1

        type_str = "YES" if type_match else "NO"
        fields_str = f"{doc_matched} / {doc_mismatched} / {doc_missing}"
        print(f"{img_filename:<30} | {type_str:<10} | {fields_str:<35}")
        
        results.append({
            "filename": img_filename,
            "type_match": type_match,
            "matched": doc_matched,
            "mismatched": doc_mismatched,
            "missing": doc_missing
        })

    print("-" * 80)
    print("OVERALL ACCURACY")
    if total_fields > 0:
        print(f"Total Fields Checked : {total_fields}")
        print(f"Matched            : {matched_fields} ({(matched_fields/total_fields)*100:.1f}%)")
        print(f"Mismatched         : {mismatched_fields} ({(mismatched_fields/total_fields)*100:.1f}%)")
        print(f"Missing            : {missing_fields} ({(missing_fields/total_fields)*100:.1f}%)")
    else:
        print("No fields checked.")
    print("\nNote: Document classification and field extraction are currently using mocked/regex fallbacks due to missing dependencies.")
    
    db.close()

if __name__ == "__main__":
    run_validation()
