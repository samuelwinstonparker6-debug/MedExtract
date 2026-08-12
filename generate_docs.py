import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

patient_name = "John Doe"
hospital_name = "City General Hospital"
date = "2023-10-27"

def create_prescription(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, hospital_name)
    c.setFont("Helvetica", 12)
    c.drawString(100, 730, f"Date: {date}")
    c.drawString(100, 710, f"Patient Name: {patient_name}")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 670, "PRESCRIPTION")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 640, "1. Amoxicillin 500mg - Take 1 tablet twice daily for 7 days")
    c.drawString(100, 620, "2. Ibuprofen 400mg - Take 1 tablet every 6 hours as needed for pain")
    
    c.drawString(100, 500, "Doctor's Signature: Dr. Sarah Smith")
    c.save()

def create_fake_prescription(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Oakwood Medical Center") # Different Hospital!
    c.setFont("Helvetica", 12)
    c.drawString(100, 730, f"Date: 2024-01-15")
    c.drawString(100, 710, f"Patient Name: Mike Fraudster") # Different Patient!
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 670, "PRESCRIPTION")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 640, "1. Oxycodone 10mg - Take 1 tablet every 4 hours for pain")
    c.drawString(100, 620, "2. Xanax 0.5mg - Take 1 tablet daily for anxiety")
    
    c.drawString(100, 500, "Doctor's Signature: Dr. Fake Person")
    c.save()

def create_invoice(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, hospital_name)
    c.setFont("Helvetica", 12)
    c.drawString(100, 730, f"Date: {date}")
    c.drawString(100, 710, f"Patient Name: {patient_name}")
    c.drawString(100, 690, "Invoice Number: INV-98765")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 650, "MEDICAL INVOICE")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 610, "Description                      Amount")
    c.drawString(100, 590, "Consultation Fee                 $150.00")
    c.drawString(100, 570, "Blood Test (CBC)                 $75.00")
    c.drawString(100, 550, "X-Ray                            $120.00")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 510, "Total Amount Due:                $345.00")
    c.save()

def create_lab_report(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, hospital_name)
    c.setFont("Helvetica", 12)
    c.drawString(100, 730, f"Date: {date}")
    c.drawString(100, 710, f"Patient Name: {patient_name}")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 670, "LABORATORY TEST REPORT")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 640, "Test Name            Result    Reference Range")
    c.setFont("Helvetica", 12)
    c.drawString(100, 620, "Hemoglobin           14.5      13.8 - 17.2 g/dL")
    c.drawString(100, 600, "White Blood Cells    6.2       4.5 - 11.0 10^3/uL")
    c.drawString(100, 580, "Platelets            250       150 - 450 10^3/uL")
    c.drawString(100, 560, "Glucose (Fasting)    95        70 - 100 mg/dL")
    
    c.drawString(100, 500, "Pathologist: Dr. Alan Grant")
    c.save()

def create_discharge_summary(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, hospital_name)
    c.setFont("Helvetica", 12)
    c.drawString(100, 730, f"Admission Date: 2023-10-25    Discharge Date: {date}")
    c.drawString(100, 710, f"Patient Name: {patient_name}")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 670, "DISCHARGE SUMMARY")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 640, "Diagnosis:")
    c.setFont("Helvetica", 12)
    c.drawString(100, 625, "Acute Bronchitis")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 595, "Treatment Provided:")
    c.setFont("Helvetica", 12)
    c.drawString(100, 580, "Intravenous antibiotics, nebulization therapy.")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 550, "Discharge Instructions:")
    c.setFont("Helvetica", 12)
    c.drawString(100, 535, "Complete oral antibiotic course. Follow up in 7 days.")
    c.save()

if __name__ == "__main__":
    os.makedirs("test_documents", exist_ok=True)
    create_prescription("test_documents/prescription.pdf")
    create_fake_prescription("test_documents/fake_prescription.pdf")
    create_invoice("test_documents/invoice.pdf")
    create_lab_report("test_documents/lab_report.pdf")
    create_discharge_summary("test_documents/discharge_summary.pdf")
    print("Documents generated successfully.")
