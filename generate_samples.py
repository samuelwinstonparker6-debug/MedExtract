import cv2
import numpy as np
import os

def create_sample_invoice():
    img = np.ones((800, 600, 3), dtype=np.uint8) * 255
    cv2.putText(img, "CITY HOSPITAL", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    cv2.putText(img, "TAX INVOICE", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
    cv2.putText(img, "Date: Oct 15, 2023", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
    cv2.putText(img, "Patient Name: John Doe", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
    cv2.putText(img, "Consultation Fee", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
    cv2.putText(img, "Total Amount: $150.00", (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
    
    cv2.imwrite("tests/sample_documents/sample_invoice.jpg", img)
    # We can use jpg instead of pdf for the invoice as well to avoid pdf2image if poppler is missing

def create_sample_prescription():
    img = np.ones((800, 600, 3), dtype=np.uint8) * 255
    cv2.putText(img, "DR. ADAMS CLINIC", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    cv2.putText(img, "RX PRESCRIPTION", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
    cv2.putText(img, "Date: Jan 10, 2024", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
    cv2.putText(img, "Patient Name: Jane Smith", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
    cv2.putText(img, "Amoxicillin 500mg", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
    cv2.putText(img, "Take 1 tablet daily", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
    
    cv2.imwrite("tests/sample_documents/sample_prescription.jpg", img)

def create_sample_lab_report():
    img = np.ones((800, 600, 3), dtype=np.uint8) * 255
    cv2.putText(img, "NATIONAL LABS", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    cv2.putText(img, "LAB REPORT", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
    cv2.putText(img, "Date: Feb 20, 2024", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
    cv2.putText(img, "Patient: Bob Jones", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
    cv2.putText(img, "Test: Complete Blood Count", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
    cv2.putText(img, "HGB Result: 13.5 g/dL", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
    cv2.putText(img, "Reference Range: 13.0 - 17.0", (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
    
    cv2.imwrite("tests/sample_documents/sample_lab_report.jpg", img)

if __name__ == '__main__':
    os.makedirs("tests/sample_documents", exist_ok=True)
    create_sample_invoice()
    create_sample_prescription()
    create_sample_lab_report()
    print("Created sample documents.")
