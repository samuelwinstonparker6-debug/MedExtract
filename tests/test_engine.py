import os
import cv2
import numpy as np
import pytest
from unittest.mock import patch, MagicMock

from app.engine.models import BoundingBox, OCRWord
from app.engine.preprocessing import normalize_resolution, deskew_image, reduce_noise_and_normalize_contrast
from app.engine.layout import analyze_layout
from app.engine.pipeline import process_document
from app.engine.extraction import extract_structured_data

@pytest.fixture
def dummy_image():
    # Create a 100x100 white image
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    # Draw a line so it's not completely blank
    cv2.line(img, (10, 50), (90, 50), (0, 0, 0), 2)
    return img

def test_normalize_resolution(dummy_image):
    # Test upscaling
    img_large = normalize_resolution(dummy_image, target_height=200)
    assert img_large.shape[0] == 200
    assert img_large.shape[1] == 200
    
def test_deskew_image(dummy_image):
    # Rotate the dummy image by 10 degrees
    center = (50, 50)
    M = cv2.getRotationMatrix2D(center, 10, 1.0)
    rotated = cv2.warpAffine(dummy_image, M, (100, 100), borderValue=(255, 255, 255))
    
    # Deskew should rotate it back (roughly)
    deskewed = deskew_image(rotated)
    assert deskewed is not None
    assert deskewed.shape[0] >= 100 # May be padded
    
def test_reduce_noise_and_contrast(dummy_image):
    processed = reduce_noise_and_normalize_contrast(dummy_image)
    assert processed.shape == dummy_image.shape
    assert processed.dtype == np.uint8

def test_analyze_layout():
    # Mock OCR words to test header/footer logic
    words = [
        OCRWord(text="Header Text", box=BoundingBox(x_min=0.1, y_min=0.05, x_max=0.5, y_max=0.08), confidence=0.9),
        OCRWord(text="Body Text", box=BoundingBox(x_min=0.1, y_min=0.5, x_max=0.5, y_max=0.55), confidence=0.9),
        OCRWord(text="Footer Text", box=BoundingBox(x_min=0.1, y_min=0.95, x_max=0.5, y_max=0.98), confidence=0.9)
    ]
    
    # Create a real dummy image file to pass to analyze_layout
    dummy_path = "test_dummy.png"
    cv2.imwrite(dummy_path, np.ones((100, 100, 3), dtype=np.uint8) * 255)
    
    try:
        regions = analyze_layout(dummy_path, words)
        types = [r.region_type for r in regions]
        assert "Header" in types
        assert "Footer" in types
    finally:
        if os.path.exists(dummy_path):
            os.remove(dummy_path)


def test_extract_structured_data_patient_name_and_amount():
    text = "Medical Invoice Patient Name: John Doe Age 34 Total Amount: ₹ 1,250.50 Invoice Date: 12/05/2025"
    result = extract_structured_data(text)

    assert result["patient_name"]["value"] == "JOHN DOE"
    assert result["amount"]["value"] == "₹ 1,250.50"
    assert result["patient_name"]["confidence"] >= 0.7
    assert result["amount"]["confidence"] >= 0.85


def test_extract_structured_data_amount_due_without_decimals():
    text = "Invoice Patient: Jane Smith Total Due: Rs 4500 Invoice Date: 01-APR-2025"
    result = extract_structured_data(text)

    assert result["patient_name"]["value"] == "JANE SMITH"
    assert result["amount"]["value"] == "RS 4500"
    assert result["amount"]["confidence"] >= 0.85


@patch("app.engine.pipeline.preprocess_for_pipeline")
@patch("app.engine.pipeline.extract_ocr_data")
@patch("app.engine.pipeline.analyze_layout")
def test_process_document(mock_layout, mock_ocr, mock_preprocess):
    dummy_path = "test_dummy_doc.png"
    cv2.imwrite(dummy_path, np.ones((100, 100, 3), dtype=np.uint8) * 255)
    
    try:
        # Mock returns
        mock_preprocess.return_value = [dummy_path]
        mock_ocr.return_value = []
        mock_layout.return_value = []
        
        doc_rep = process_document(dummy_path, "test_123")
        
        assert doc_rep.document_id == "test_123"
        assert len(doc_rep.pages) == 1
        assert doc_rep.pages[0].page_number == 1
        assert doc_rep.pages[0].original_width == 100
        assert doc_rep.pages[0].original_height == 100
        assert mock_preprocess.called
        assert mock_ocr.called
        assert mock_layout.called
    finally:
        if os.path.exists(dummy_path):
            os.remove(dummy_path)
