from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from app.engine.models import DocumentRepresentation
from app.engine.risk_models import RiskAssessment
from app.engine.explanation_models import ExplanationResult
from app.engine.explanation_engine import generate_explanation

router = APIRouter(prefix="/api/v2/explanation", tags=["explanation"])

class ExplanationRequest(BaseModel):
    document_representation: DocumentRepresentation
    reference_representation: DocumentRepresentation
    risk_assessment: RiskAssessment

@router.post("/generate")
def create_explanation(request: ExplanationRequest) -> ExplanationResult:
    """
    Generate a visual side-by-side explanation identifying stable structures
    and highlighting explicitly altered text (e.g. potential fraud tampering).
    """
    try:
        # Generate the explanation and visual bounding box overlay
        result = generate_explanation(
            doc_rep=request.document_representation,
            ref_rep=request.reference_representation,
            risk_assessment=request.risk_assessment,
            output_dir="static/visuals"  # Assume a static dir exists to serve images
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation generation failed: {str(e)}")
