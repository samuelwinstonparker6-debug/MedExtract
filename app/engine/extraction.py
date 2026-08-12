"""
Extraction Module for MedExtract V2
Responsible for extracting structured information (Patient Name, Amount, Date)
using a lightweight LLM/NLP model rather than brittle regex.
"""

import logging
import re

logger = logging.getLogger(__name__)

def extract_structured_data(text_content: str, image_path: str = None) -> dict:
    """
    Extracts entities using heuristics and regex for Phase 1.
    """
    logger.info("Extracting structured data via heuristic engine")
    
    if not text_content:
        text_content = ""
        
    text_content = text_content.upper()
    
    # Defaults
    result = {
        "amount": {"value": None, "confidence": 0.0},
        "invoice_date": {"value": None, "confidence": 0.0},
        "provider_name": {"value": None, "confidence": 0.0},
        "patient_name": {"value": None, "confidence": 0.0},
        "license_number": {"value": None, "confidence": 0.0}
    }
    
    # 1. Amount Extraction
    amount_keywords = [
        r"(?:TOTAL AMOUNT|GRAND TOTAL|AMOUNT PAYABLE|NET AMOUNT|AMOUNT DUE|TOTAL DUE|BILL AMOUNT|TOTAL)\s*[:\-]?\s*([₹₹RS\.]*\s*\d[\d,]*(?:\.\d{1,2})?)",
        r"(?:AMOUNT|TOTAL)\s*[:\-]?\s*([₹₹RS\.]*\s*\d[\d,]*(?:\.\d{1,2})?)"
    ]
    
    for pattern in amount_keywords:
        match = re.search(pattern, text_content)
        if match:
            result["amount"] = {"value": match.group(1).strip(), "confidence": 0.85}
            break
            
    # 2. Date Extraction
    date_patterns = [
        r"(?:DATE|INVOICE DATE|DATE OF)\s*[:\-]?\s*(\d{2}[-/]\d{2}[-/]\d{4})",
        r"(?:DATE|INVOICE DATE|DATE OF)\s*[:\-]?\s*(\d{2}-[A-Z]{3}-\d{4})",
        r"(?:DATE|INVOICE DATE|DATE OF)\s*([A-Z]{3}\s*\d+)",
        r"(\d{2}[-/]\d{2}[-/]\d{4})",
        r"(\d{2}-[A-Z]{3}-\d{4})"
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text_content)
        if match:
            result["invoice_date"] = {"value": match.group(1).strip(), "confidence": 0.90}
            break
            
    # 3. Patient Name
    patient_patterns = [
        r"(?:PATIENT|PATENT)\s*NAME\s*[:\-]?\s*([A-Z][A-Z0-9\s\.\-\/,&']{1,80}?)\s*(?=AGE|SEX|GENDER|DOB|DATE|ADDRESS|TOTAL|INVOICE|AMOUNT|LICENSE|LICENCE|ID|GST|PAN|PROVIDER|DOCTOR|$)",
        r"(?:PATIENT|PATENT)\s*[:\-]?\s*([A-Z][A-Z0-9\s\.\-\/,&']{1,80}?)\s*(?=AGE|SEX|GENDER|DOB|DATE|ADDRESS|TOTAL|INVOICE|AMOUNT|LICENSE|LICENCE|ID|GST|PAN|PROVIDER|DOCTOR|$)",
        r"NAME\s*[:\-]?\s*([A-Z][A-Z0-9\s\.\-\/,&']{1,80}?)\s*(?=AGE|SEX|GENDER|DOB|DATE|ADDRESS|TOTAL|INVOICE|AMOUNT|LICENSE|LICENCE|ID|GST|PAN|PROVIDER|DOCTOR|$)"
    ]
    for pattern in patient_patterns:
        match = re.search(pattern, text_content)
        if match:
            result["patient_name"] = {"value": match.group(1).strip(), "confidence": 0.70}
            break

    # 4. License Number
    license_patterns = [
        r"(?:LICENSE|LICENCE)\s*(?:KEY|NO|NUMBER)?\s*[:\-]?\s*([A-Z0-9]+)",
    ]
    for pattern in license_patterns:
        match = re.search(pattern, text_content)
        if match:
            result["license_number"] = {"value": match.group(1).strip(), "confidence": 0.80}
            break

    # 5. Basic Provider
    # Grab text up to "MEDICAL INVOICE" or "TAX INVOICE" if available.
    match = re.search(r"^(.*?)(?:MEDICAL INVOICE|TAX INVOICE|INVOICE)", text_content)
    if match:
        # Strip some leading garbage if present
        prov_text = match.group(1).strip()
        prov_text = re.sub(r"^INVOKE NO INV \d+\s+\d+\s+DATE OF [A-Z]+\s+\d+\s*", "", prov_text)
        result["provider_name"] = {"value": prov_text[:50].strip(), "confidence": 0.60}
    else:
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        if len(lines) > 0:
            result["provider_name"] = {"value": lines[0][:50], "confidence": 0.50}
        
    return result
