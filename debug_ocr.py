import os, pytesseract
from PIL import Image

# Find tesseract
tess_paths = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\DELL\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
]
for p in tess_paths:
    if os.path.exists(p):
        pytesseract.pytesseract.tesseract_cmd = p
        break

img_path = r"c:\Users\DELL\Desktop\Baja Finserv Health Pvt. Ltd\MedExtract\hospital_bill_praneeth.png"
text = pytesseract.image_to_string(Image.open(img_path))
print("--- OCR TEXT START ---")
print(text)
print("--- OCR TEXT END ---")

from app.services.extractor import extract_invoice_fields, get_entities
fields = extract_invoice_fields(text, get_entities(text))
print("--- EXTRACTED FIELDS ---")
print(fields)
