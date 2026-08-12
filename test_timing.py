import time
import os
import shutil
import logging
from app.core.database import SessionLocal
from app.models.domain import Document
from app.services.ocr import process_document_ocr

logging.basicConfig(level=logging.INFO)

def test_timing():
    db = SessionLocal()
    
    # Ensure sunrise.png exists
    if not os.path.exists("sunrise.png"):
        print("Please run test_sunrise.py first.")
        return
        
    shutil.copy("sunrise.png", "app/uploads/sunrise_timing.png")
    
    doc = Document(
        filename="sunrise_timing.png",
        file_path="app/uploads/sunrise_timing.png",
        status="uploaded"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    print(f"\n--- Starting Processing for Document {doc.id} (COLD START) ---")
    start_time = time.time()
    process_document_ocr(doc.id)
    end_time = time.time()
    print(f"Total Processing Time (COLD START): {end_time - start_time:.2f} seconds")

    print(f"\n--- Starting Processing for Document {doc.id} (HOT START) ---")
    start_time = time.time()
    process_document_ocr(doc.id)
    end_time = time.time()
    print(f"Total Processing Time (HOT START): {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    test_timing()
