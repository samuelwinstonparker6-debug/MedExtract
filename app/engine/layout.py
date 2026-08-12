import logging
import cv2
import numpy as np
from typing import List

try:
    from pyzbar.pyzbar import decode
except ImportError:
    decode = None

from app.engine.models import DocumentRegion, BoundingBox, OCRWord

logger = logging.getLogger(__name__)


def generate_structural_embedding(image_path: str) -> list[float]:
    """
    Generates a high-dimensional structural embedding representing the spatial layout of the document.
    (Stub implementation for Phase 1 architectural restructuring)
    """
    logger.info(f"Generating structural embedding for {image_path}")
    # Return a dummy vector for now
    return [0.0] * 512


def analyze_layout(image_path: str, ocr_words: List[OCRWord]) -> List[DocumentRegion]:
    """
    Performs heuristic-based basic document layout analysis.
    Finds Headers, Footers, Tables, Images/Logos, and Barcodes.
    """
    regions = []
    
    img = cv2.imread(image_path)
    if img is None:
        return regions
        
    h, w = img.shape[:2]
    
    # 1. Headers and Footers (based on OCR box positions)
    for word in ocr_words:
        if word.box.y_max < 0.1:
            regions.append(DocumentRegion(
                region_type="Header",
                box=word.box,
                content=word.text,
                confidence=0.9
            ))
        elif word.box.y_min > 0.9:
            regions.append(DocumentRegion(
                region_type="Footer",
                box=word.box,
                content=word.text,
                confidence=0.9
            ))

    # 2. Barcodes / QR Codes
    if decode:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        barcodes = decode(gray)
        for barcode in barcodes:
            (x, y, bw, bh) = barcode.rect
            bbox = BoundingBox(
                x_min=x / w,
                y_min=y / h,
                x_max=(x + bw) / w,
                y_max=(y + bh) / h
            )
            regions.append(DocumentRegion(
                region_type="Barcode",
                box=bbox,
                content=barcode.data.decode("utf-8"),
                confidence=1.0
            ))
            
    # 3. Simple Table Detection (Find horizontal and vertical lines)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    thresh = cv2.adaptiveThreshold(
        cv2.bitwise_not(gray), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2
    )
    
    horizontal = np.copy(thresh)
    cols = horizontal.shape[1]
    horizontal_size = cols // 30
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
    horizontal = cv2.erode(horizontal, horizontalStructure)
    horizontal = cv2.dilate(horizontal, horizontalStructure)

    vertical = np.copy(thresh)
    rows = vertical.shape[0]
    vertical_size = rows // 30
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vertical_size))
    vertical = cv2.erode(vertical, verticalStructure)
    vertical = cv2.dilate(vertical, verticalStructure)

    table_mask = cv2.add(horizontal, vertical)
    contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for c in contours:
        x, y, bw, bh = cv2.boundingRect(c)
        # Minimum table size
        if bw > w * 0.3 and bh > h * 0.05:
            bbox = BoundingBox(
                x_min=x / w,
                y_min=y / h,
                x_max=(x + bw) / w,
                y_max=(y + bh) / h
            )
            regions.append(DocumentRegion(
                region_type="Table",
                box=bbox,
                confidence=0.8
            ))

    return regions
