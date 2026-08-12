import logging
from typing import List
import cv2

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

import pytesseract
from app.engine.models import OCRWord, BoundingBox

logger = logging.getLogger(__name__)

_ocr_engine = None

def get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None and PaddleOCR is not None:
        try:
            logger.info("Initializing PaddleOCR (CPU)...")
            _ocr_engine = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=False)
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
    return _ocr_engine


def extract_ocr_data(image_path: str) -> List[OCRWord]:
    """
    Extracts text and normalized bounding boxes from an image using PaddleOCR or Tesseract.
    """
    engine = get_ocr_engine()
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image for OCR: {image_path}")
        
    h, w = img.shape[:2]
    if h == 0 or w == 0:
        return []

    ocr_words = []
    
    # Try PaddleOCR first
    if engine is not None:
        logger.info(f"Running PaddleOCR on {image_path}")
        result = engine.ocr(image_path, cls=True)
        if result and result[0]:
            for line in result[0]:
                box_points = line[0]
                text_tuple = line[1]
                text, confidence = text_tuple[0], float(text_tuple[1])
                x_coords = [point[0] for point in box_points]
                y_coords = [point[1] for point in box_points]
                
                x_min, y_min = max(0.0, min(x_coords) / w), max(0.0, min(y_coords) / h)
                x_max, y_max = min(1.0, max(x_coords) / w), min(1.0, max(y_coords) / h)
                
                if x_max > x_min and y_max > y_min:
                    ocr_words.append(OCRWord(text=text, box=BoundingBox(x_min=x_min, y_min=y_min, x_max=x_max, y_max=y_max), confidence=confidence))
            return ocr_words

    # Fallback to Tesseract
    logger.info(f"Running Tesseract fallback on {image_path}")
    import os
    from app.core.config import settings
    # For Windows dev, configure tesseract executable if set
    tess_cmd = getattr(settings, 'TESSERACT_CMD', None)
    if tess_cmd and os.path.exists(tess_cmd):
        pytesseract.pytesseract.tesseract_cmd = tess_cmd

    try:
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            if int(data['conf'][i]) > 0 and text:
                x_min = max(0.0, float(data['left'][i]) / w)
                y_min = max(0.0, float(data['top'][i]) / h)
                x_max = min(1.0, float(data['left'][i] + data['width'][i]) / w)
                y_max = min(1.0, float(data['top'][i] + data['height'][i]) / h)
                if x_max > x_min and y_max > y_min:
                    ocr_words.append(OCRWord(
                        text=text, 
                        box=BoundingBox(x_min=x_min, y_min=y_min, x_max=x_max, y_max=y_max), 
                        confidence=float(data['conf'][i]) / 100.0
                    ))
    except Exception as e:
        logger.error(f"Tesseract OCR failed: {e}")
        
    return ocr_words
