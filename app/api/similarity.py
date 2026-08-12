from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import numpy as np
from pydantic import BaseModel

from app.engine.models import MatchResult, TemplateFingerprint
from app.engine.faiss_index import engine as faiss_engine
from app.engine.vectorizer import vectorize_structural_fingerprint, generate_visual_embedding

router = APIRouter(prefix="/api/v2/similarity", tags=["similarity"])


class DocumentUploadRequest(BaseModel):
    document_id: str
    structural_fingerprint: TemplateFingerprint
    image_path: Optional[str] = None  # To generate visual embedding if desired


@router.post("/document")
def search_similar_documents(request: DocumentUploadRequest) -> List[MatchResult]:
    """
    POST document to find similar templates using FAISS.
    """
    s_vec = vectorize_structural_fingerprint(request.structural_fingerprint)
    
    v_vec = None
    if request.image_path:
        v_vec = generate_visual_embedding(request.image_path)
        
    results = faiss_engine.search_top_k(s_vec, v_vec, k=5)
    
    match_results = []
    for r in results:
        match_results.append(MatchResult(
            document_id=request.document_id,
            matched_document_id=r["matched_document_id"],
            similarity_score=r["similarity_score"],
            structural_similarity=r["structural_similarity"],
            visual_similarity=r["visual_similarity"],
            embedding_similarity=r["embedding_similarity"],
            confidence=r["confidence"]
        ))
        
    return match_results


@router.get("/{document_id}/similar")
def get_similar_documents(document_id: str) -> List[MatchResult]:
    """
    Retrieve similar documents for an already indexed document.
    """
    if document_id not in faiss_engine.reverse_id_map:
        raise HTTPException(status_code=404, detail="Document not found in index")
        
    faiss_idx = faiss_engine.reverse_id_map[document_id]
    s_vec = faiss_engine.structural_index.reconstruct(faiss_idx)
    
    v_vec = None
    if faiss_engine.visual_index.ntotal > faiss_idx:
        try:
            v_vec = faiss_engine.visual_index.reconstruct(faiss_idx)
        except Exception:
            pass
            
    # Search including self
    results = faiss_engine.search_top_k(s_vec, v_vec, k=6)
    
    match_results = []
    for r in results:
        # Filter out self
        if r["matched_document_id"] != document_id:
            match_results.append(MatchResult(
                document_id=document_id,
                matched_document_id=r["matched_document_id"],
                similarity_score=r["similarity_score"],
                structural_similarity=r["structural_similarity"],
                visual_similarity=r["visual_similarity"],
                embedding_similarity=r["embedding_similarity"],
                confidence=r["confidence"]
            ))
            
    return match_results


@router.get("/cluster/{cluster_id}")
def get_template_cluster(cluster_id: str):
    """
    Placeholder for retrieving all docs within a certain distance from a centroid.
    Currently returns a 501 Not Implemented.
    """
    raise HTTPException(status_code=501, detail="Cluster retrieval not yet implemented")


@router.post("/rebuild")
def rebuild_index():
    """
    Clears the FAISS index. (In a real system, this would then trigger a background job to re-add from DB).
    """
    faiss_engine.rebuild_index()
    return {"status": "success", "message": "Index rebuilt (cleared). Ready for document ingestion."}
