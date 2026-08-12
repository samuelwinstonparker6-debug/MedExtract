import logging
import math
import numpy as np
from typing import List, Dict
from app.engine.models import TemplateFingerprint

logger = logging.getLogger(__name__)

def cosine_similarity_list(vec1: List[float], vec2: List[float]) -> float:
    """Computes cosine similarity between two lists of floats."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    
    # Use numpy for speed
    v1 = np.array(vec1, dtype=float)
    v2 = np.array(vec2, dtype=float)
    
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 == 0 or norm2 == 0:
        # If both are exactly 0, they are technically identical zero-vectors
        return 1.0 if norm1 == norm2 else 0.0
        
    return float(np.dot(v1, v2) / (norm1 * norm2))


def cosine_similarity(vec1, vec2) -> float:
    """Robust wrapper for cosine similarity that accepts lists, numpy arrays, or stringified lists."""
    if isinstance(vec1, str):
        try:
            import json
            vec1 = json.loads(vec1)
        except Exception:
            try:
                vec1 = eval(vec1)
            except Exception:
                return 0.0
                
    if isinstance(vec2, str):
        try:
            import json
            vec2 = json.loads(vec2)
        except Exception:
            try:
                vec2 = eval(vec2)
            except Exception:
                return 0.0

    if not isinstance(vec1, (list, np.ndarray)) or not isinstance(vec2, (list, np.ndarray)):
        return 0.0

    v1 = vec1.tolist() if isinstance(vec1, np.ndarray) else list(vec1)
    v2 = vec2.tolist() if isinstance(vec2, np.ndarray) else list(vec2)

    return cosine_similarity_list(v1, v2)


def euclidean_distance(p1: List[float], p2: List[float]) -> float:
    """Computes euclidean distance between two 2D points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def calculate_fingerprint_similarity(fp1: TemplateFingerprint, fp2: TemplateFingerprint) -> float:
    """
    Computes a composite structural similarity score [0.0, 1.0] between two TemplateFingerprints.
    Weighting:
    - 50% Spatial Grid Density
    - 20% X-Alignment Histogram
    - 20% Y-Alignment Histogram
    - 10% Region Anchors & Whitespace
    """
    grid_sim = cosine_similarity_list(fp1.spatial_grid, fp2.spatial_grid)
    x_hist_sim = cosine_similarity_list(fp1.x_alignment_hist, fp2.x_alignment_hist)
    y_hist_sim = cosine_similarity_list(fp1.y_alignment_hist, fp2.y_alignment_hist)
    
    # Calculate region anchor penalty
    # If a region exists in both, calculate distance. If it's missing in one, apply a small penalty.
    region_score = 1.0
    all_keys = set(fp1.region_centroids.keys()).union(set(fp2.region_centroids.keys()))
    
    if all_keys:
        penalties = 0.0
        for k in all_keys:
            if k in fp1.region_centroids and k in fp2.region_centroids:
                dist = euclidean_distance(fp1.region_centroids[k], fp2.region_centroids[k])
                # Max distance in 1x1 normalized space is sqrt(2) ~ 1.414
                penalties += min(1.0, dist) 
            else:
                penalties += 0.5 # Missing region penalty
                
        # Average penalty mapped to a 0-1 score
        region_score = max(0.0, 1.0 - (penalties / len(all_keys)))
        
    # Whitespace ratio difference penalty
    ws_diff = abs(fp1.whitespace_ratio - fp2.whitespace_ratio)
    ws_score = max(0.0, 1.0 - ws_diff)
    
    # Combine the structural anchors and whitespace
    structural_score = (region_score * 0.7) + (ws_score * 0.3)
    
    final_score = (grid_sim * 0.5) + (x_hist_sim * 0.2) + (y_hist_sim * 0.2) + (structural_score * 0.1)
    
    return float(final_score)


class SimilarityEngineWrapper:
    """Wrapper that adapts the FAISS index engine to the interface expected by the pipeline and test suites."""
    def __init__(self):
        from app.engine.faiss_index import engine
        self._engine = engine

    def generate_combined_vector(self, fingerprint: TemplateFingerprint, image_path: str = None) -> tuple[np.ndarray, np.ndarray]:
        from app.engine.vectorizer import vectorize_structural_fingerprint, generate_visual_embedding
        s_vec = vectorize_structural_fingerprint(fingerprint)
        v_vec = None
        if image_path:
            v_vec = generate_visual_embedding(image_path)
        else:
            # 1000-d zero vector if visual embedding is skipped
            v_vec = np.zeros(1000, dtype=np.float32)
        return s_vec, v_vec

    def add_document_to_index(self, document_id: str, combined_vector: tuple[np.ndarray, np.ndarray]):
        s_vec, v_vec = combined_vector
        self._engine.add_template(document_id, s_vec, v_vec)

    def search(self, combined_vector: tuple[np.ndarray, np.ndarray], top_k: int = 5) -> list[tuple[str, float]]:
        s_vec, v_vec = combined_vector
        results = self._engine.search_top_k(s_vec, v_vec, k=top_k)
        # Expects distance (where lower = closer, exact = 0.0)
        return [(r["matched_document_id"], 1.0 - r["similarity_score"]) for r in results]


def get_similarity_engine():
    return SimilarityEngineWrapper()

