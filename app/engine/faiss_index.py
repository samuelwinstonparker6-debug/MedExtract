import os
import faiss
import numpy as np
import logging
import pickle
from typing import List, Tuple, Dict, Optional

logger = logging.getLogger(__name__)

class SimilarityEngine:
    def __init__(self, index_path: str = "template_index"):
        """
        Manages two FAISS indices:
        1. Structural Index (140-d) - High priority, layout focused
        2. Visual Index (1000-d) - Fallback, pixel focused
        """
        self.structural_dim = 140
        self.visual_dim = 1000
        
        # FAISS inner product index (Cosine similarity if normalized)
        self.structural_index = faiss.IndexFlatIP(self.structural_dim)
        self.visual_index = faiss.IndexFlatIP(self.visual_dim)
        
        # Maps FAISS integer IDs (0, 1, 2...) to string document_ids
        self.id_map: Dict[int, str] = {}
        self.reverse_id_map: Dict[str, int] = {}
        self.current_id = 0
        
        self.storage_dir = os.path.join(os.getcwd(), "data", index_path)
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self._load_indices()

    def _load_indices(self):
        s_path = os.path.join(self.storage_dir, "structural.faiss")
        v_path = os.path.join(self.storage_dir, "visual.faiss")
        m_path = os.path.join(self.storage_dir, "id_map.pkl")
        
        if os.path.exists(s_path) and os.path.exists(m_path):
            try:
                self.structural_index = faiss.read_index(s_path)
                if os.path.exists(v_path):
                    self.visual_index = faiss.read_index(v_path)
                    
                with open(m_path, "rb") as f:
                    data = pickle.load(f)
                    self.id_map = data.get("id_map", {})
                    self.current_id = data.get("current_id", 0)
                    # build reverse map
                    self.reverse_id_map = {v: k for k, v in self.id_map.items()}
                logger.info(f"Loaded FAISS indices with {self.structural_index.ntotal} vectors.")
            except Exception as e:
                logger.error(f"Failed to load FAISS indices: {e}")

    def save_indices(self):
        s_path = os.path.join(self.storage_dir, "structural.faiss")
        v_path = os.path.join(self.storage_dir, "visual.faiss")
        m_path = os.path.join(self.storage_dir, "id_map.pkl")
        
        faiss.write_index(self.structural_index, s_path)
        faiss.write_index(self.visual_index, v_path)
        
        with open(m_path, "wb") as f:
            pickle.dump({
                "id_map": self.id_map,
                "current_id": self.current_id
            }, f)

    def rebuild_index(self):
        """Clears the indices. Should be followed by re-adding all documents."""
        self.structural_index = faiss.IndexFlatIP(self.structural_dim)
        self.visual_index = faiss.IndexFlatIP(self.visual_dim)
        self.id_map = {}
        self.reverse_id_map = {}
        self.current_id = 0
        self.save_indices()

    def add_template(self, document_id: str, structural_vec: np.ndarray, visual_vec: Optional[np.ndarray] = None):
        """Adds a document to the index."""
        if document_id in self.reverse_id_map:
            logger.warning(f"Document {document_id} already exists in FAISS. Skipping.")
            return

        idx = self.current_id
        
        # Reshape for FAISS
        s_vec = structural_vec.reshape(1, -1).astype(np.float32)
        self.structural_index.add(s_vec)
        
        if visual_vec is not None and len(visual_vec) == self.visual_dim:
            v_vec = visual_vec.reshape(1, -1).astype(np.float32)
            self.visual_index.add(v_vec)
        else:
            # Add a zero vector if visual embedding is missing to keep indices synchronized
            self.visual_index.add(np.zeros((1, self.visual_dim), dtype=np.float32))
            
        self.id_map[idx] = document_id
        self.reverse_id_map[document_id] = idx
        self.current_id += 1
        
        # Save on every update (suitable for incremental up to ~10k. 
        # For larger scales, do this async or periodically).
        self.save_indices()

    def search_top_k(self, structural_vec: np.ndarray, visual_vec: Optional[np.ndarray], k: int = 5) -> List[Dict]:
        """
        Retrieves top-K similar templates. 
        Calculates composite similarity heavily weighting structural.
        """
        if self.structural_index.ntotal == 0:
            return []

        # FAISS search expects shape (n_queries, d)
        s_query = structural_vec.reshape(1, -1).astype(np.float32)
        
        # Retrieve slightly more from structural to account for reranking
        search_k = min(k * 2, self.structural_index.ntotal)
        
        # structural_distances is actually inner-product = cosine similarity (since normalized)
        structural_distances, structural_indices = self.structural_index.search(s_query, search_k)
        
        results = []
        for i in range(search_k):
            faiss_idx = int(structural_indices[0][i])
            if faiss_idx < 0 or faiss_idx not in self.id_map:
                continue
                
            doc_id = self.id_map[faiss_idx]
            s_sim = float(structural_distances[0][i])
            
            # Fetch visual vector for this faiss_idx
            # FAISS IndexFlatIP allows reconstructing vectors
            v_sim = 0.0
            if visual_vec is not None and self.visual_index.ntotal > faiss_idx:
                try:
                    db_v_vec = self.visual_index.reconstruct(faiss_idx)
                    # Compute inner product manually for the visual vector
                    v_sim = float(np.dot(visual_vec, db_v_vec))
                except Exception:
                    pass
            
            # Composite similarity: 80% structural, 20% visual (or 100% structural if visual_vec is None)
            if visual_vec is not None:
                composite_sim = (s_sim * 0.8) + (v_sim * 0.2)
            else:
                composite_sim = s_sim
            
            confidence = composite_sim # Can be tuned with a sigmoid later
            
            results.append({
                "matched_document_id": doc_id,
                "similarity_score": composite_sim,
                "structural_similarity": s_sim,
                "visual_similarity": v_sim,
                "embedding_similarity": composite_sim, 
                "confidence": confidence
            })
            
        # Sort by composite score descending
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:k]

# Global instance
engine = SimilarityEngine()
