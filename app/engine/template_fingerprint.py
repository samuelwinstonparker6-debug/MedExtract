import logging
import numpy as np
from typing import List, Dict, Tuple
from app.engine.models import DocumentRepresentation, TemplateFingerprint, BoundingBox

logger = logging.getLogger(__name__)


def generate_fingerprint(doc: DocumentRepresentation) -> TemplateFingerprint:
    """
    Transforms a DocumentRepresentation into a purely structural TemplateFingerprint.
    Ignores raw text. Focuses on:
    - Spatial density grid (10x10)
    - Alignment histograms (X and Y)
    - Relative Region Centroids
    - Whitespace ratio
    """
    if not doc.pages:
        return TemplateFingerprint()
        
    # We will compute the fingerprint based on the first page primarily, 
    # as most templates (invoices/prescriptions) establish their identity on page 1.
    page = doc.pages[0]
    
    spatial_grid, whitespace_ratio = _generate_spatial_grid(page.words)
    x_hist, y_hist = _generate_alignment_histograms(page.words)
    centroids = _extract_region_centroids(page.regions)
    
    return TemplateFingerprint(
        spatial_grid=spatial_grid,
        x_alignment_hist=x_hist,
        y_alignment_hist=y_hist,
        region_centroids=centroids,
        whitespace_ratio=whitespace_ratio
    )


def _generate_spatial_grid(words: List) -> Tuple[List[float], float]:
    """
    Divides the page into a 10x10 grid.
    Calculates the density of bounding box area in each grid cell.
    Returns the flattened grid (100 values) and the overall whitespace ratio.
    """
    grid = np.zeros((10, 10), dtype=float)
    total_text_area = 0.0
    
    if not words:
        return grid.flatten().tolist(), 1.0

    for word in words:
        box: BoundingBox = word.box
        total_text_area += (box.width * box.height)
        
        # Calculate which grid cells this box intersects
        # Normalized coordinates [0, 1], grid indices [0, 9]
        x_start = max(0, int(box.x_min * 10))
        x_end = min(9, int(box.x_max * 10))
        y_start = max(0, int(box.y_min * 10))
        y_end = min(9, int(box.y_max * 10))
        
        area_contribution = (box.width * box.height) / max(1, ((x_end - x_start + 1) * (y_end - y_start + 1)))
        
        for i in range(y_start, y_end + 1):
            for j in range(x_start, x_end + 1):
                grid[i, j] += area_contribution

    # Normalize grid so sum equals 1 (handles varying amounts of text dynamically)
    grid_sum = np.sum(grid)
    if grid_sum > 0:
        grid = grid / grid_sum
        
    whitespace_ratio = max(0.0, 1.0 - total_text_area)
    return grid.flatten().tolist(), float(whitespace_ratio)


def _generate_alignment_histograms(words: List) -> Tuple[List[float], List[float]]:
    """
    Creates histograms of the X (left-aligned) and Y (row-aligned) coordinates.
    Bins into 20 buckets (5% precision) to capture the underlying layout grid.
    """
    x_hist = np.zeros(20, dtype=float)
    y_hist = np.zeros(20, dtype=float)
    
    if not words:
        return x_hist.tolist(), y_hist.tolist()
        
    for word in words:
        box: BoundingBox = word.box
        
        # Left alignment X bin
        x_bin = min(19, int(box.x_min * 20))
        x_hist[x_bin] += 1
        
        # Row alignment Y bin (using center Y)
        center_y = box.y_min + (box.height / 2)
        y_bin = min(19, int(center_y * 20))
        y_hist[y_bin] += 1
        
    # Normalize
    x_sum = np.sum(x_hist)
    if x_sum > 0:
        x_hist = x_hist / x_sum
        
    y_sum = np.sum(y_hist)
    if y_sum > 0:
        y_hist = y_hist / y_sum
        
    return x_hist.tolist(), y_hist.tolist()


def _extract_region_centroids(regions: List) -> Dict[str, list[float]]:
    """
    Extracts the centroids (x,y) of detected semantic regions.
    If multiple regions of the same type exist, it averages them (e.g. multiple tables).
    """
    centroids = {}
    type_counts = {}
    
    for region in regions:
        rtype = region.region_type
        box: BoundingBox = region.box
        cx = box.x_min + (box.width / 2)
        cy = box.y_min + (box.height / 2)
        
        if rtype not in centroids:
            centroids[rtype] = [0.0, 0.0]
            type_counts[rtype] = 0
            
        centroids[rtype][0] += cx
        centroids[rtype][1] += cy
        type_counts[rtype] += 1
        
    # Average them
    for rtype in centroids:
        centroids[rtype][0] /= type_counts[rtype]
        centroids[rtype][1] /= type_counts[rtype]
        
    return centroids
