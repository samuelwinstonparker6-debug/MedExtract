import os
import cv2
import uuid
import logging
from typing import List, Tuple
from app.engine.models import DocumentRepresentation, BoundingBox
from app.engine.risk_models import RiskAssessment
from app.engine.explanation_models import ExplanationResult, VisualRegion
from app.core.config import settings

logger = logging.getLogger(__name__)

def _calculate_iou(box1: BoundingBox, box2: BoundingBox) -> float:
    """Calculates Intersection over Union (IoU) of two bounding boxes."""
    x_left = max(box1.x_min, box2.x_min)
    y_top = max(box1.y_min, box2.y_min)
    x_right = min(box1.x_max, box2.x_max)
    y_bottom = min(box1.y_max, box2.y_max)
    
    if x_right < x_left or y_bottom < y_top:
        return 0.0
        
    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    box1_area = box1.width * box1.height
    box2_area = box2.width * box2.height
    
    iou = intersection_area / float(box1_area + box2_area - intersection_area)
    return iou


def generate_explanation(
    doc_rep: DocumentRepresentation,
    ref_rep: DocumentRepresentation,
    risk_assessment: RiskAssessment,
    output_dir: str = "visuals"
) -> ExplanationResult:
    """
    Compares a submitted document with a reference template to generate visual explanations.
    Produces a side-by-side image with Red/Green bounding boxes.
    """
    if not doc_rep.pages or not ref_rep.pages:
        return ExplanationResult(
            original_document_id=doc_rep.document_id,
            matched_template_id=ref_rep.document_id,
            risk_assessment=risk_assessment
        )
        
    doc_page = doc_rep.pages[0]
    ref_page = ref_rep.pages[0]
    
    stable_regions: List[VisualRegion] = []
    changed_regions: List[VisualRegion] = []
    
    # 1. Structural Region Matching
    # Find matching layout regions (Tables, Headers, etc)
    for ref_reg in ref_page.regions:
        matched = False
        for doc_reg in doc_page.regions:
            if doc_reg.region_type == ref_reg.region_type:
                iou = _calculate_iou(doc_reg.box, ref_reg.box)
                if iou > 0.7:  # High structural overlap
                    matched = True
                    stable_regions.append(VisualRegion(
                        region_type=doc_reg.region_type,
                        box=doc_reg.box,
                        status="MATCH",
                        description=f"Stable {doc_reg.region_type} Structure"
                    ))
                    break
                    
    # 2. Dynamic Text Matching
    # Check if text in similar bounding boxes has completely changed
    for doc_word in doc_page.words:
        # Simple heuristic: is there a word in the reference in the exact same spot?
        # If yes, do the strings match?
        found_overlap = False
        text_matches = False
        
        for ref_word in ref_page.words:
            iou = _calculate_iou(doc_word.box, ref_word.box)
            if iou > 0.5:
                found_overlap = True
                # Case insensitive string comparison
                if doc_word.text.strip().lower() == ref_word.text.strip().lower():
                    text_matches = True
                break
                
        if found_overlap and not text_matches:
            # The structure exists, but the content changed! (e.g. Provider name, Amount)
            changed_regions.append(VisualRegion(
                region_type="Altered Text",
                box=doc_word.box,
                status="CHANGED",
                description=f"Content altered to: '{doc_word.text}'"
            ))
            
    # 3. Generate Image
    image_url = None
    if doc_page.image_path and ref_page.image_path and os.path.exists(doc_page.image_path) and os.path.exists(ref_page.image_path):
        try:
            image_url = _create_side_by_side_visual(
                doc_page.image_path,
                ref_page.image_path,
                stable_regions,
                changed_regions,
                output_dir
            )
        except Exception as e:
            logger.error(f"Visual comparison image generation failed: {e}")
            
    return ExplanationResult(
        original_document_id=doc_rep.document_id,
        matched_template_id=ref_rep.document_id,
        risk_assessment=risk_assessment,
        visual_comparison_image_url=image_url,
        stable_regions=stable_regions,
        changed_regions=changed_regions
    )


def _create_side_by_side_visual(
    doc_img_path: str,
    ref_img_path: str,
    stable_regions: List[VisualRegion],
    changed_regions: List[VisualRegion],
    output_dir: str
) -> str:
    """
    Creates a CPU-friendly side-by-side comparison image.
    Draws green boxes for stable regions and red boxes for changed regions on the original doc.
    """
    doc_img = cv2.imread(doc_img_path)
    ref_img = cv2.imread(ref_img_path)
    
    if doc_img is None or ref_img is None:
        raise ValueError("Could not read images for visual comparison.")
        
    h1, w1 = doc_img.shape[:2]
    h2, w2 = ref_img.shape[:2]
    
    # Resize ref image to match doc image height for hconcat
    target_h = h1
    target_w = int(w2 * (h1 / h2))
    ref_img_resized = cv2.resize(ref_img, (target_w, target_h))
    
    # Draw on doc image
    overlay = doc_img.copy()
    
    # Draw Stable (Green)
    for reg in stable_regions:
        x1 = int(reg.box.x_min * w1)
        y1 = int(reg.box.y_min * h1)
        x2 = int(reg.box.x_max * w1)
        y2 = int(reg.box.y_max * h1)
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), -1) # Filled green
        
    # Draw Changed (Red)
    for reg in changed_regions:
        x1 = int(reg.box.x_min * w1)
        y1 = int(reg.box.y_min * h1)
        x2 = int(reg.box.x_max * w1)
        y2 = int(reg.box.y_max * h1)
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 255), -1) # Filled red
        
    # Alpha blend overlay
    alpha = 0.3
    cv2.addWeighted(overlay, alpha, doc_img, 1 - alpha, 0, doc_img)
    
    # Draw explicit borders for changed regions (fully opaque red borders)
    for reg in changed_regions:
        x1 = int(reg.box.x_min * w1)
        y1 = int(reg.box.y_min * h1)
        x2 = int(reg.box.x_max * w1)
        y2 = int(reg.box.y_max * h1)
        cv2.rectangle(doc_img, (x1, y1), (x2, y2), (0, 0, 255), 3) 
        
    # Concatenate side by side (Doc on Left, Reference on Right)
    combined = cv2.hconcat([doc_img, ref_img_resized])
    
    # Add text labels
    cv2.putText(combined, "Submitted Claim", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(combined, "Matched Reference Template", (w1 + 20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    os.makedirs(output_dir, exist_ok=True)
    out_filename = f"comparison_{uuid.uuid4().hex[:8]}.jpg"
    out_path = os.path.join(output_dir, out_filename)
    
    cv2.imwrite(out_path, combined)
    
    return f"/static/visuals/{out_filename}"
