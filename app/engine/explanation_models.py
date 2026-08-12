from pydantic import BaseModel, Field
from typing import List, Optional
from app.engine.models import BoundingBox
from app.engine.risk_models import RiskAssessment

class VisualRegion(BaseModel):
    """
    Represents a specific structural or textual region to be highlighted in the UI.
    """
    region_type: str = Field(..., description="e.g., 'Header', 'Provider Name', 'Table'")
    box: BoundingBox
    status: str = Field(..., description="'MATCH' (Green) or 'CHANGED' (Red)")
    description: Optional[str] = None

class ExplanationResult(BaseModel):
    """
    The final explainability payload delivered to the frontend.
    Combines the Risk Assessment with visual bounding box data.
    """
    original_document_id: str
    matched_template_id: str
    risk_assessment: RiskAssessment
    
    # URL to the generated side-by-side or overlay comparison image
    visual_comparison_image_url: Optional[str] = None
    
    stable_regions: List[VisualRegion] = Field(default_factory=list)
    changed_regions: List[VisualRegion] = Field(default_factory=list)
