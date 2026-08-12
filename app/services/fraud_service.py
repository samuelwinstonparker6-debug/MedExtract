"""
fraud_service.py
------------------
Core fraud detection pipeline executed on every uploaded document (Version 2).

Uses Vector Embeddings (structural layouts) and Cosine Similarity
rather than brittle heuristics.
"""

import logging
import re
import time
from sqlalchemy.orm import Session
from app.models.domain import Document, ProviderReference

from app.engine.similarity import cosine_similarity

logger = logging.getLogger(__name__)


def _normalize_provider_name(name: str) -> str:
    if not name:
        return ""
    value = str(name).lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def provider_names_match(claimed_name: str, reference_name: str) -> bool:
    """Return True when two provider labels refer to the same provider brand.

    This deliberately tolerates OCR / template phrasing differences such as:
    - 'BAJAJ FINSERV HEALTH PVT. LTD ORIGINAL PROVIDER'
    - 'Original Hospital Template - Bajaj Finserv Health'
    """
    claimed = _normalize_provider_name(claimed_name)
    reference = _normalize_provider_name(reference_name)

    if not claimed or not reference:
        return False
    if claimed == reference:
        return True
    if claimed in reference or reference in claimed:
        return True

    generic_tokens = {
        "original", "template", "provider", "providers", "copy", "claim",
        "submission", "hospital", "hospitals", "clinic", "clinics",
        "care", "diagnostics", "medical", "health", "invoice", "invoices",
        "pvt", "ltd", "limited", "doc", "docs", "document", "documents"
    }

    claimed_tokens = [t for t in claimed.split() if t and t not in generic_tokens]
    ref_tokens = [t for t in reference.split() if t and t not in generic_tokens]

    if not claimed_tokens or not ref_tokens:
        return False

    claimed_set = set(claimed_tokens)
    ref_set = set(ref_tokens)
    common = claimed_set & ref_set
    if common:
        return True

    # Short names that share a core brand token (e.g., 'bajaj finserv' vs 'bajaj finserv health')
    claimed_phrase = " ".join(claimed_tokens)
    ref_phrase = " ".join(ref_tokens)
    return claimed_phrase in ref_phrase or ref_phrase in claimed_phrase


def check_document_for_fraud(db: Session, document_id: int) -> tuple[str, float, list[str]]:
    """
    Main entry point called by the background worker.
    Returns: (fraud_status, max_fraud_score, fraud_flags)
    """
    target_doc = db.query(Document).filter(Document.id == document_id).first()
    if not target_doc:
        return "NONE", 0.0, []

    target_embedding = None
    if hasattr(target_doc, 'structural_embedding') and target_doc.structural_embedding:
        target_embedding = target_doc.structural_embedding
    else:
        # Reconstruct embedding from FAISS index
        try:
            from app.engine.faiss_index import engine as faiss_engine
            doc_str_id = str(document_id)
            if doc_str_id in faiss_engine.reverse_id_map:
                faiss_idx = faiss_engine.reverse_id_map[doc_str_id]
                target_embedding = faiss_engine.structural_index.reconstruct(faiss_idx)
        except Exception as e:
            logger.error(f"Failed to reconstruct structural embedding from FAISS for doc {document_id}: {e}")

    if target_embedding is None:
        # Fallback if no embedding generated
        return "NONE", 0.0, []

    flags: list[str] = []
    max_fraud_score: float = 0.0
    fraud_status: str = "NONE"

    # Stub extraction of claimed provider (to be replaced by proper engine extraction later)
    t_provider = ""
    if target_doc.structured_data and "provider_name" in target_doc.structured_data:
        val = target_doc.structured_data["provider_name"]
        t_provider = val.get("value", "") if isinstance(val, dict) else val

    # ──────────────────────────────────────────────────────────────────────────
    # LAYER 1 — Golden Template pixel-level verification (Deprecated in V2)
    # ──────────────────────────────────────────────────────────────────────────
    # if t_provider:
    #     golden = db.query(GoldenTemplate).filter(GoldenTemplate.provider_name.ilike(f"%{t_provider}%")).first()
    #     if golden and golden.file_path:
    #         import os
    #         if os.path.exists(golden.file_path):
    #             visual_score = verify_document_against_golden_template(target_doc.file_path, golden.file_path)
    #             target_doc.visual_integrity_score = visual_score
    #             if visual_score < 0.98:
    #                 flags.append("Golden Template Mismatch: Template layout forgery detected.")
    #                 max_fraud_score = max(max_fraud_score, 0.99)
    #                 fraud_status = "RED"

    # ──────────────────────────────────────────────────────────────────────────
    # LAYER 2 — Provider Reference Template Matching (Vector Search)
    # ──────────────────────────────────────────────────────────────────────────
    all_refs = db.query(ProviderReference).all()
    best_match_score = 0.0

    for ref in all_refs:
        ref_embedding = []
        if hasattr(ref, 'template_embedding') and ref.template_embedding:
            ref_embedding = ref.template_embedding
        elif hasattr(ref, 'fingerprint_data') and ref.fingerprint_data:
            try:
                import json
                from app.engine.models import TemplateFingerprint
                from app.engine.vectorizer import vectorize_structural_fingerprint
                
                fp_dict = json.loads(ref.fingerprint_data) if isinstance(ref.fingerprint_data, str) else ref.fingerprint_data
                if "spatial_grid" in fp_dict:
                    fp = TemplateFingerprint(**fp_dict)
                    ref_embedding = vectorize_structural_fingerprint(fp)
            except Exception as e:
                logger.error(f"Failed to parse fingerprint_data for provider ref {ref.id}: {e}")
                
        if ref_embedding is None or len(ref_embedding) == 0:
            continue
            
        sim = cosine_similarity(target_embedding, ref_embedding)
        if sim > best_match_score:
            best_match_score = sim
            
        if sim >= 0.95:
            # High similarity to a reference template
            ref_label = (ref.label or "").strip().lower()
            claimed_lower = (t_provider or "").strip().lower()
            
            is_same_provider = False
            if claimed_lower and (claimed_lower in ref_label or ref_label in claimed_lower):
                is_same_provider = True
                
            if provider_names_match(claimed_lower, ref_label):
                target_doc.reference_verification_result = f"Verified Authentic — Matched to: {ref.label}"
            else:
                fraud_status = "RED"
                max_fraud_score = max(max_fraud_score, sim)
                flags.append(f"RED FLAG: Template cloned from {ref.label}")

    final_score = max(max_fraud_score, best_match_score)
    return fraud_status, float(round(final_score, 4)), flags
