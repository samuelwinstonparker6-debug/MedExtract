import cv2
import numpy as np
import time
import easyocr
import os

def create_sunrise_invoice():
    img = np.ones((800, 800, 3), dtype=np.uint8) * 255
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    cv2.putText(img, "Sunrise Health Medical Center", (50, 100), font, 1.2, (0, 0, 0), 2)
    cv2.putText(img, "Medical Invoice", (50, 150), font, 1.0, (0, 0, 0), 1)
    cv2.putText(img, "License: 1234", (50, 200), font, 0.8, (0, 0, 0), 1)
    cv2.putText(img, "Patient: Bob", (50, 250), font, 0.8, (0, 0, 0), 1)
    cv2.putText(img, "Date: 2026-08-01", (50, 300), font, 0.8, (0, 0, 0), 1)
    cv2.putText(img, "Total Amount Due: $350.00", (50, 350), font, 0.8, (0, 0, 0), 1)
    
    cv2.imwrite("sunrise.png", img)
    print("Created sunrise.png")

if __name__ == "__main__":
    create_sunrise_invoice()
    
    print("Initializing EasyOCR...")
    reader = easyocr.Reader(['en'], verbose=False)
    
    print("\n--- OCR on RAW IMAGE ---")
    results = reader.readtext("sunrise.png")
    raw_text = "\n".join([r[1] for r in results])
    print(raw_text)
    
    print("\n--- OCR on PREPROCESSED IMAGE (Current Logic) ---")
    from app.services.preprocessing import preprocess_image
    processed_path = preprocess_image("sunrise.png")
    results = reader.readtext(processed_path)
    processed_text = "\n".join([r[1] for r in results])
    print(processed_text)
