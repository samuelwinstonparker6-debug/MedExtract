import cv2
import numpy as np
import os

def create_invoice_template(provider_name, patient_name, total_amount, date_val):
    # Create a blank white image (800x1000)
    img = np.ones((1000, 800, 3), dtype=np.uint8) * 255
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Common Template Elements (these will be exact same bounding boxes if text lengths are similar)
    # Header
    cv2.putText(img, "MEDICAL INVOICE", (250, 100), font, 1.2, (0, 0, 0), 2)
    
    # Provider Info box
    cv2.rectangle(img, (50, 150), (400, 250), (0, 0, 0), 2)
    cv2.putText(img, "PROVIDER INFO", (60, 180), font, 0.7, (50, 50, 50), 1)
    cv2.putText(img, provider_name, (60, 220), font, 0.9, (0, 0, 0), 2)
    
    # Patient Info box
    cv2.rectangle(img, (450, 150), (750, 250), (0, 0, 0), 2)
    cv2.putText(img, "PATIENT INFO", (460, 180), font, 0.7, (50, 50, 50), 1)
    cv2.putText(img, patient_name, (460, 220), font, 0.9, (0, 0, 0), 2)
    
    # Date
    cv2.putText(img, f"Date: {date_val}", (50, 320), font, 0.8, (0, 0, 0), 1)
    
    # Table Header
    cv2.line(img, (50, 360), (750, 360), (0, 0, 0), 2)
    cv2.putText(img, "Description", (60, 390), font, 0.8, (0, 0, 0), 1)
    cv2.putText(img, "Amount", (600, 390), font, 0.8, (0, 0, 0), 1)
    cv2.line(img, (50, 410), (750, 410), (0, 0, 0), 2)
    
    # Table Items
    cv2.putText(img, "Consultation Fee", (60, 450), font, 0.8, (0, 0, 0), 1)
    cv2.putText(img, "$100.00", (600, 450), font, 0.8, (0, 0, 0), 1)
    
    cv2.putText(img, "Lab Tests", (60, 500), font, 0.8, (0, 0, 0), 1)
    cv2.putText(img, "$150.00", (600, 500), font, 0.8, (0, 0, 0), 1)
    
    # Total
    cv2.line(img, (50, 550), (750, 550), (0, 0, 0), 2)
    cv2.putText(img, f"TOTAL: {total_amount}", (550, 590), font, 1.0, (0, 0, 0), 2)
    
    # Footer
    cv2.putText(img, "Thank you for your business.", (220, 900), font, 0.7, (100, 100, 100), 1)
    
    return img

if __name__ == "__main__":
    os.makedirs("tests/fraud_samples", exist_ok=True)
    
    # 1. Authentic Document
    img1 = create_invoice_template("City Hospital", "John Doe", "$250.00", "2023-10-01")
    cv2.imwrite("tests/fraud_samples/auth_city_hosp.png", img1)
    print("Created auth_city_hosp.png")
    
    # 2. Authentic Document (different template layout)
    # Just draw some stuff differently
    img2 = np.ones((1000, 800, 3), dtype=np.uint8) * 255
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img2, "GENERIC LABS INVOICE", (100, 100), font, 1.2, (0, 0, 0), 2)
    cv2.putText(img2, "Patient: Jane Smith", (100, 200), font, 1.0, (0, 0, 0), 1)
    cv2.putText(img2, "Total: $120.00", (100, 300), font, 1.0, (0, 0, 0), 1)
    cv2.imwrite("tests/fraud_samples/auth_generic_labs.png", img2)
    print("Created auth_generic_labs.png")
    
    # 3. Fraudulent Document - Amber Flag
    # Exact same pixel template as img1, but different patient.
    img3 = create_invoice_template("City Hospital", "Mike Ty", "$250.00", "2023-10-05")
    cv2.imwrite("tests/fraud_samples/fraud_amber_mike.png", img3)
    print("Created fraud_amber_mike.png")
    
    # 4. Fraudulent Document - Red Flag
    # Exact same pixel template as img1, but completely DIFFERENT provider name.
    # Fraudster reused the "City Hospital" template to fake a "Fake Clinic" bill.
    img4 = create_invoice_template("Fake Clinic", "Alice Smith", "$250.00", "2023-10-10")
    cv2.imwrite("tests/fraud_samples/fraud_red_fake.png", img4)
    print("Created fraud_red_fake.png")
    
    print("Dataset generated successfully.")
