import pytest
from app.engine.models import DocumentRepresentation, PageRepresentation, BoundingBox, DocumentRegion, OCRWord
from app.engine.risk_models import RiskAssessment, RiskLevel
from app.engine.explanation_engine import generate_explanation

def create_mock_doc(doc_id: str, provider_text: str) -> DocumentRepresentation:
    words = [
        OCRWord(text=provider_text, box=BoundingBox(x_min=0.1, y_min=0.1, x_max=0.4, y_max=0.15), confidence=0.9),
        OCRWord(text="Invoice", box=BoundingBox(x_min=0.8, y_min=0.1, x_max=0.9, y_max=0.15), confidence=0.9),
    ]
    regions = [
        DocumentRegion(region_type="Header", box=BoundingBox(x_min=0.05, y_min=0.05, x_max=0.95, y_max=0.2)),
        DocumentRegion(region_type="Table", box=BoundingBox(x_min=0.1, y_min=0.3, x_max=0.9, y_max=0.8))
    ]
    page = PageRepresentation(
        page_number=1,
        image_path="", # Empty path skips image generation in test
        original_width=800,
        original_height=1000,
        words=words,
        regions=regions
    )
    return DocumentRepresentation(document_id=doc_id, pages=[page])

def test_generate_explanation():
    # Original template: "Clinic A"
    ref_rep = create_mock_doc("ref_doc", "Clinic A")
    
    # Cloned template: "Scam Clinic B" (Same structure, different text)
    doc_rep = create_mock_doc("fraud_doc", "Scam Clinic B")
    
    risk = RiskAssessment(
        risk_score=100.0,
        risk_level=RiskLevel.RED,
        confidence=0.95,
        reasons=["Template Cloning"],
        evidence=["Provider differs"]
    )
    
    result = generate_explanation(doc_rep, ref_rep, risk)
    
    # 1. Structural matches
    # Should identify "Header" and "Table" as stable regions
    stable_types = [r.region_type for r in result.stable_regions]
    assert "Header" in stable_types
    assert "Table" in stable_types
    assert len(result.stable_regions) == 2
    
    # 2. Changed regions (Altered Text)
    # It should detect that the text "Scam Clinic B" replaced "Clinic A" in the same bounding box
    assert len(result.changed_regions) == 1
    assert result.changed_regions[0].status == "CHANGED"
    assert "Scam Clinic B" in result.changed_regions[0].description
