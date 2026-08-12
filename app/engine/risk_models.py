from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class RiskLevel(str, Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"

class ClaimMetadata(BaseModel):
    """
    Contextual business metadata accompanying the document submission.
    Used by the Risk Engine to distinguish legitimate reuse from fraud.
    """
    provider_name: str
    patient_name: str
    amount: float
    document_date: str
    invoice_number: Optional[str] = None

class RiskAssessment(BaseModel):
    """
    The final output of the Fraud Risk Engine.
    """
    risk_score: float = Field(..., ge=0.0, le=100.0, description="0-100 risk score")
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0.0, le=1.0)
    
    # Human-readable explanations
    reasons: List[str] = Field(default_factory=list, description="Top-level reasons for the flag")
    evidence: List[str] = Field(default_factory=list, description="Specific visual/structural evidence points")
    
    # Traceability
    matched_documents: List[str] = Field(default_factory=list, description="IDs of similar docs found")
    matched_template_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "risk_score": 92.5,
                "risk_level": "RED",
                "confidence": 0.96,
                "reasons": ["Potential Fraudulent Reuse", "Suspicious Similarity"],
                "evidence": [
                    "Same table geometry",
                    "Same header placement",
                    "Provider name differs",
                    "Amount differs"
                ],
                "matched_documents": ["doc_1234"],
                "matched_template_id": "tpl_XYZ"
            }
        }
