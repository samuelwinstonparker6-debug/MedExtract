import pytest
import numpy as np
import os
from app.engine.faiss_index import SimilarityEngine

@pytest.fixture
def engine():
    # Use a fresh index for tests
    eng = SimilarityEngine(index_path="test_index")
    eng.rebuild_index()
    yield eng
    eng.rebuild_index() # Cleanup
    
def generate_mock_structural_vector(base: float = 0.5) -> np.ndarray:
    vec = np.ones(140, dtype=np.float32) * base
    # Normalize
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec

def test_faiss_identical_templates(engine):
    vec_a = generate_mock_structural_vector(0.5)
    
    engine.add_template("doc_identical_1", vec_a)
    engine.add_template("doc_identical_2", vec_a)
    
    # Query with the exact same vector
    results = engine.search_top_k(vec_a, None, k=2)
    assert len(results) == 2
    # Inner product of identical normalized vectors should be ~1.0
    assert results[0]["similarity_score"] > 0.99
    assert results[1]["similarity_score"] > 0.99
    
def test_faiss_unrelated_templates(engine):
    # Template A is flat 0.5
    vec_a = generate_mock_structural_vector(0.5)
    
    # Template B is flat -0.5 (orthogonal-ish)
    vec_b = generate_mock_structural_vector(-0.5)
    
    engine.add_template("doc_A", vec_a)
    engine.add_template("doc_B", vec_b)
    
    # Query with A, expecting A to be near 1.0, and B to be far
    results = engine.search_top_k(vec_a, None, k=2)
    
    doc_a_res = next(r for r in results if r["matched_document_id"] == "doc_A")
    doc_b_res = next(r for r in results if r["matched_document_id"] == "doc_B")
    
    assert doc_a_res["similarity_score"] > 0.99
    assert doc_b_res["similarity_score"] < 0.1 # Should be highly dissimilar (-1.0 technically for opposite, but structural sim computes differently depending on the weights)
    
def test_faiss_near_duplicate_templates(engine):
    vec_a = generate_mock_structural_vector(0.5)
    
    # Add a small amount of noise to simulate slightly shifted bounding boxes
    noise = np.random.normal(0, 0.05, 140).astype(np.float32)
    vec_a_noisy = vec_a + noise
    norm = np.linalg.norm(vec_a_noisy)
    vec_a_noisy = vec_a_noisy / norm
    
    engine.add_template("doc_base", vec_a)
    engine.add_template("doc_noisy", vec_a_noisy)
    
    results = engine.search_top_k(vec_a, None, k=2)
    doc_noisy_res = next(r for r in results if r["matched_document_id"] == "doc_noisy")
    
    # Should still be highly confident (e.g. > 0.9) but not exactly 1.0
    assert 0.90 < doc_noisy_res["similarity_score"] < 1.0
