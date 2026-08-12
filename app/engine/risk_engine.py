import logging
from typing import List
from app.engine.models import MatchResult
from app.engine.risk_models import RiskAssessment, RiskLevel, ClaimMetadata
import app.engine.risk_config as config

logger = logging.getLogger(__name__)

def evaluate_risk(
    claim_meta: ClaimMetadata,
    match_results: List[MatchResult],
    reference_templates: dict # Mocks DB: { "doc_id": ClaimMetadata }
) -> RiskAssessment:
    """
    Evaluates the contextual risk of a document submission based on structural similarity
    and metadata comparison.
    """
    
    if not match_results:
        # First of its kind, no template matches
        return RiskAssessment(
            risk_score=config.SCORE_BASE_GREEN,
            risk_level=RiskLevel.GREEN,
            confidence=0.9,
            reasons=[config.REASON_LEGITIMATE],
            evidence=["No structurally similar documents found in database"]
        )

    # Focus on the highest match
    best_match = match_results[0]
    matched_doc_id = best_match.matched_document_id
    
    # In a real system, we fetch the historical claim metadata for `matched_doc_id` from the DB.
    # Here we simulate it with the `reference_templates` dictionary.
    ref_meta: ClaimMetadata = reference_templates.get(matched_doc_id)
    
    risk_score = 0.0
    reasons = []
    evidence = []
    
    # 1. Start with structural basis
    struct_sim = best_match.structural_similarity
    
    if struct_sim > config.SIM_THRESH_HIGH:
        evidence.append(config.EVIDENCE_SAME_STRUCT)
        
        if ref_meta:
            # Check metadata context
            provider_match = (claim_meta.provider_name.lower() == ref_meta.provider_name.lower())
            patient_match = (claim_meta.patient_name.lower() == ref_meta.patient_name.lower())
            amount_match = (claim_meta.amount == ref_meta.amount)
            
            if not provider_match:
                # Same template, different provider -> RED FLAG (Template Cloning)
                risk_score += config.SCORE_BASE_RED
                risk_score += config.PENALTY_DIFFERENT_PROVIDER
                reasons.append(config.REASON_TEMPLATE_CLONE)
                evidence.append(config.EVIDENCE_DIFF_PROVIDER)
            else:
                evidence.append(config.EVIDENCE_SAME_PROVIDER)
                if patient_match and amount_match:
                    # Same template, provider, patient, amount -> DUPLICATE CLAIM
                    risk_score += config.SCORE_BASE_AMBER
                    risk_score += config.PENALTY_EXACT_DUPLICATE
                    reasons.append(config.REASON_DUPLICATE)
                    evidence.append(config.EVIDENCE_SAME_PATIENT)
                    evidence.append(config.EVIDENCE_SAME_AMOUNT)
                else:
                    # Same provider, different patient -> Legitimate Reuse
                    risk_score = config.SCORE_BASE_GREEN
                    reasons.append(config.REASON_LEGITIMATE)
                    evidence.append(config.EVIDENCE_DIFF_PATIENT)
    
    elif struct_sim > config.SIM_THRESH_SUSPICIOUS:
        # Generic Template (e.g., standard Word document used by many)
        risk_score += config.SCORE_BASE_AMBER
        reasons.append(config.REASON_GENERIC)
        evidence.append("Moderately similar layout detected")
        if ref_meta and claim_meta.provider_name.lower() != ref_meta.provider_name.lower():
             evidence.append("Potentially generic template shared across different providers")
    else:
        # Low similarity
        risk_score = config.SCORE_BASE_GREEN
        reasons.append("Unique Document Layout")
        evidence.append("No high-risk structural matches")

    # Add visual evidence if available
    if best_match.visual_similarity > config.VISUAL_THRESH_HIGH:
        evidence.append(config.EVIDENCE_SAME_VISUAL)

    # Clamp score to 100
    risk_score = min(100.0, max(0.0, risk_score))
    
    # Assign level based on final clamped score
    if risk_score >= 80:
        level = RiskLevel.RED
    elif risk_score >= 40:
        level = RiskLevel.AMBER
    else:
        level = RiskLevel.GREEN
        
    return RiskAssessment(
        risk_score=risk_score,
        risk_level=level,
        confidence=best_match.confidence,
        reasons=reasons,
        evidence=evidence,
        matched_documents=[matched_doc_id],
        matched_template_id=f"tpl_{matched_doc_id[:8]}"
    )
