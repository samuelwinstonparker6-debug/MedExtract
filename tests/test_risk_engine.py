import pytest
from app.engine.models import MatchResult
from app.engine.risk_models import ClaimMetadata, RiskLevel
from app.engine.risk_engine import evaluate_risk
from app.services.fraud_service import provider_names_match
import app.engine.risk_config as config

def test_legitimate_reuse():
    # Structurally identical, Same Provider, Different Patient (Legitimate Reuse)
    claim = ClaimMetadata(provider_name="Clinic A", patient_name="John Doe", amount=100.0, document_date="2024-01-01")
    ref = ClaimMetadata(provider_name="Clinic A", patient_name="Jane Doe", amount=200.0, document_date="2024-01-02")
    match = MatchResult(
        document_id="doc_new",
        matched_document_id="doc_ref",
        similarity_score=0.99,
        structural_similarity=0.99,
        visual_similarity=0.90,
        embedding_similarity=0.99,
        confidence=0.99
    )
    
    assessment = evaluate_risk(claim, [match], {"doc_ref": ref})
    
    assert assessment.risk_level == RiskLevel.GREEN
    assert assessment.risk_score == config.SCORE_BASE_GREEN
    assert config.REASON_LEGITIMATE in assessment.reasons
    assert config.EVIDENCE_DIFF_PATIENT in assessment.evidence

def test_fraudulent_template_cloning():
    # Structurally identical, DIFFERENT Provider (Fraudulent Cloning)
    claim = ClaimMetadata(provider_name="Scam Clinic B", patient_name="John Doe", amount=5000.0, document_date="2024-01-01")
    ref = ClaimMetadata(provider_name="Real Hospital A", patient_name="Jane Doe", amount=200.0, document_date="2024-01-02")
    match = MatchResult(
        document_id="doc_new",
        matched_document_id="doc_ref",
        similarity_score=0.99,
        structural_similarity=0.99,
        visual_similarity=0.50, # Different logo/name lowers visual sim slightly
        embedding_similarity=0.99,
        confidence=0.99
    )
    
    assessment = evaluate_risk(claim, [match], {"doc_ref": ref})
    
    assert assessment.risk_level == RiskLevel.RED
    assert assessment.risk_score >= 100.0 # Base(80) + Penalty(40) = 120 -> clamped to 100
    assert config.REASON_TEMPLATE_CLONE in assessment.reasons
    assert config.EVIDENCE_DIFF_PROVIDER in assessment.evidence

def test_exact_duplicate():
    # Structurally identical, Same Provider, Same Patient, Same Amount (Duplicate)
    claim = ClaimMetadata(provider_name="Clinic A", patient_name="John Doe", amount=100.0, document_date="2024-01-01")
    ref = ClaimMetadata(provider_name="Clinic A", patient_name="John Doe", amount=100.0, document_date="2024-01-01")
    match = MatchResult(
        document_id="doc_new",
        matched_document_id="doc_ref",
        similarity_score=0.99,
        structural_similarity=0.99,
        visual_similarity=0.99,
        embedding_similarity=0.99,
        confidence=0.99
    )
    
    assessment = evaluate_risk(claim, [match], {"doc_ref": ref})
    
    # Should be AMBER/RED depending on weights. Base(50) + Penalty(30) = 80 -> RED
    assert assessment.risk_level == RiskLevel.RED 
    assert config.REASON_DUPLICATE in assessment.reasons
    assert config.EVIDENCE_SAME_AMOUNT in assessment.evidence

def test_generic_template():
    # Moderately similar (0.88), Different Provider -> Likely just a generic Quickbooks template
    claim = ClaimMetadata(provider_name="Clinic B", patient_name="John Doe", amount=100.0, document_date="2024-01-01")
    ref = ClaimMetadata(provider_name="Clinic A", patient_name="Jane Doe", amount=200.0, document_date="2024-01-02")
    match = MatchResult(
        document_id="doc_new",
        matched_document_id="doc_ref",
        similarity_score=0.88,
        structural_similarity=0.88,
        visual_similarity=0.40,
        embedding_similarity=0.88,
        confidence=0.88
    )
    
    assessment = evaluate_risk(claim, [match], {"doc_ref": ref})
    
    assert assessment.risk_level == RiskLevel.AMBER
    assert assessment.risk_score == config.SCORE_BASE_AMBER
    assert config.REASON_GENERIC in assessment.reasons


def test_original_provider_brand_names_are_treated_as_same_provider():
    # Original hospital template should not be flagged as a cloned template
    # even when the extracted OCR provider label is phrased differently.
    assert provider_names_match(
        "BAJAJ FINSERV HEALTH PVT. LTD ORIGINAL PROVIDER",
        "Original Hospital Template - Bajaj Finserv Health",
    )
