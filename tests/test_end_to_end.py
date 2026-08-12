import pytest
import os
import shutil
import numpy as np
from app.engine.models import DocumentRepresentation, PageRepresentation
from app.engine.fingerprint import generate_template_fingerprint
from app.engine.similarity import get_similarity_engine

# E2E Final Evaluation Test
# 
# The IEEE problem statement: "Similar Document Template Matching Algorithm"
# 
# Scenario:
# - Document A: The golden template structure (e.g., Hospital A Invoice)
# - Document B: A fraudulent document where text is heavily changed (amounts, names) 
#               but the physical borders, table geometries, and layout remain the same.
# - Document C: A completely different structure (e.g., Lab Report from Hospital B).
#
# Goal:
# Verify that structurally similar documents (A and B) map tightly in vector space,
# while structurally disparate documents (A and C) do not.

def create_mock_doc(doc_id: str, box_count: int, offset: float = 0.0) -> DocumentRepresentation:
    """Creates a mock document with artificial layout regions to simulate OCR/OpenCV output."""
    # We construct a document with `box_count` boxes.
    # The offset slightly shifts the structure to simulate minor scan imperfections
    regions = []
    for i in range(box_count):
        regions.append({
            "type": "table_cell",
            "x": 0.1 + offset, 
            "y": 0.1 + (i * 0.05) + offset,
            "w": 0.8,
            "h": 0.04
        })
    
    page = PageRepresentation(
        page_number=1,
        image_path="dummy.png",
        original_width=1000,
        original_height=1500,
        words=[], # Words (text) are intentionally empty since structural fingerprinting ignores them!
        regions=regions
    )
    
    return DocumentRepresentation(
        document_id=doc_id,
        pages=[page]
    )

def test_template_similarity_and_fraud_detection():
    # 1. Initialize Similarity Engine
    engine = get_similarity_engine()
    
    # 2. Setup the Documents
    # Document A (Original)
    doc_A = create_mock_doc("doc_A", 10)
    fp_A = generate_template_fingerprint(doc_A)
    
    # Document B (Forged/Cloned Template)
    # The text changed, but our mock doesn't care about text.
    # We add a 0.001 offset to simulate a slight scan misalignment
    doc_B = create_mock_doc("doc_B", 10, offset=0.001)
    fp_B = generate_template_fingerprint(doc_B)
    
    # Document C (Different Template)
    # It has a totally different layout (25 rows instead of 10, different y-spacing)
    doc_C = create_mock_doc("doc_C", 25, offset=0.2)
    fp_C = generate_template_fingerprint(doc_C)
    
    # 3. Generate Vectors
    # Note: image_path is dummy, so visual_embedding is skipped/zeroed. 
    # This purely tests the structural layout embedder.
    vec_A = engine.generate_combined_vector(fp_A, "dummy_A.png")
    vec_B = engine.generate_combined_vector(fp_B, "dummy_B.png")
    vec_C = engine.generate_combined_vector(fp_C, "dummy_C.png")
    
    # Add A to index (acting as the golden template base)
    engine.add_document_to_index("doc_A", vec_A)
    
    # 4. Perform Search
    # Search for B
    matches_B = engine.search(vec_B, top_k=1)
    assert len(matches_B) == 1
    match_b_id, match_b_score = matches_B[0]
    
    # Search for C
    matches_C = engine.search(vec_C, top_k=1)
    assert len(matches_C) == 1
    match_c_id, match_c_score = matches_C[0]
    
    # 5. Assertions matching the core problem statement
    assert match_b_id == "doc_A", "Document B should match Document A"
    assert match_c_id == "doc_A", "Document C technically matches A (since A is the only item in DB)"
    
    # The L2 Distance score for B should be significantly lower (closer to 0) than C
    # Meaning B is HIGHLY similar to A, and C is LOW similarity to A.
    assert match_b_score < match_c_score, "Document B must be mathematically closer to A than C is to A"
    
    # If match_score (L2 Distance) is small, similarity is HIGH
    print(f"Similarity Score A->B (Structural Forgery): {match_b_score}")
    print(f"Similarity Score A->C (Different Template): {match_c_score}")
    
    # For FAISS L2, exact match is 0.0
    assert match_b_score < 0.1, "Document B should have very low L2 distance (high similarity) to A"
    assert match_c_score > 0.5, "Document C should have a high L2 distance (low similarity) to A"
