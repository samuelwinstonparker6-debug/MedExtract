import pytest
from app.engine.models import DocumentRepresentation, PageRepresentation, OCRWord, BoundingBox, DocumentRegion
from app.engine.template_fingerprint import generate_fingerprint
from app.engine.similarity import calculate_fingerprint_similarity

def create_synthetic_doc(doc_id: str, text_content: str, logo_offset: float = 0.0, layout_shift: float = 0.0) -> DocumentRepresentation:
    """
    Helper to generate a mock document with specific structural layout characteristics.
    `layout_shift` alters the grid structure significantly (simulating a different template).
    `logo_offset` slightly shifts the logo (simulating minor template variances or different logo).
    `text_content` changes the textual values but keeps them in the same structural place.
    """
    # Header row
    words = [
        OCRWord(text=f"Hospital {text_content}", box=BoundingBox(x_min=0.1+layout_shift, y_min=0.05, x_max=0.4+layout_shift, y_max=0.08), confidence=0.9),
        OCRWord(text=f"Invoice {text_content}", box=BoundingBox(x_min=0.7+layout_shift, y_min=0.05, x_max=0.9+layout_shift, y_max=0.08), confidence=0.9)
    ]
    # Body rows (table-like structure)
    words.extend([
        OCRWord(text=f"Patient {text_content}", box=BoundingBox(x_min=0.1+layout_shift, y_min=0.2, x_max=0.3+layout_shift, y_max=0.22), confidence=0.9),
        OCRWord(text=f"Amount {text_content}", box=BoundingBox(x_min=0.8+layout_shift, y_min=0.2, x_max=0.9+layout_shift, y_max=0.22), confidence=0.9),
        OCRWord(text="Consultation", box=BoundingBox(x_min=0.1+layout_shift, y_min=0.25, x_max=0.4+layout_shift, y_max=0.27), confidence=0.9),
        OCRWord(text="$100", box=BoundingBox(x_min=0.8+layout_shift, y_min=0.25, x_max=0.9+layout_shift, y_max=0.27), confidence=0.9)
    ])
    
    regions = [
        DocumentRegion(region_type="Header", box=BoundingBox(x_min=0.1+layout_shift, y_min=0.05, x_max=0.9+layout_shift, y_max=0.1)),
        DocumentRegion(region_type="Logo", box=BoundingBox(x_min=0.05+logo_offset, y_min=0.02, x_max=0.15+logo_offset, y_max=0.09))
    ]
    
    page = PageRepresentation(
        page_number=1,
        image_path="",
        original_width=1000,
        original_height=1500,
        words=words,
        regions=regions
    )
    return DocumentRepresentation(document_id=doc_id, pages=[page])


def test_fingerprint_synthetic_scenarios():
    # Base template
    doc_base = create_synthetic_doc("base", "A")
    fp_base = generate_fingerprint(doc_base)
    
    # A. Same template + different text
    doc_a = create_synthetic_doc("a", "B")
    fp_a = generate_fingerprint(doc_a)
    sim_a = calculate_fingerprint_similarity(fp_base, fp_a)
    assert sim_a > 0.98, f"Test A failed: {sim_a}"
    
    # B. Same template + different logo (slightly shifted region)
    doc_b = create_synthetic_doc("b", "A", logo_offset=0.02)
    fp_b = generate_fingerprint(doc_b)
    sim_b = calculate_fingerprint_similarity(fp_base, fp_b)
    assert sim_b > 0.90, f"Test B failed: {sim_b}"
    
    # C. Same template + different provider (different text, but same layout)
    doc_c = create_synthetic_doc("c", "ProviderXYZ")
    fp_c = generate_fingerprint(doc_c)
    sim_c = calculate_fingerprint_similarity(fp_base, fp_c)
    assert sim_c > 0.98, f"Test C failed: {sim_c}"
    
    # E & F. Different template + similar text or different layout (shifted layout)
    doc_ef = create_synthetic_doc("ef", "A", layout_shift=0.3)
    fp_ef = generate_fingerprint(doc_ef)
    sim_ef = calculate_fingerprint_similarity(fp_base, fp_ef)
    assert sim_ef < 0.60, f"Test E/F failed: {sim_ef}"
    
    # Proving structural similarity matters more than textual similarity:
    # doc_a (different text, same structure) should have higher similarity than doc_ef (same text, diff structure)
    assert sim_a > sim_ef
