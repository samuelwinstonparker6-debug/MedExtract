from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class BoundingBox(BaseModel):
    """
    Normalized bounding box coordinates (0.0 to 1.0).
    """
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min


class OCRWord(BaseModel):
    """
    A single word or phrase detected by OCR.
    """
    text: str
    box: BoundingBox
    confidence: float


class DocumentRegion(BaseModel):
    """
    A specific semantic region detected in the document layout.
    Types might include: 'Header', 'Footer', 'Table', 'Image', 'Barcode', 'TextParagraph'
    """
    region_type: str
    box: BoundingBox
    content: Optional[str] = None
    confidence: float = 1.0


class PageRepresentation(BaseModel):
    """
    Representation of a single rendered page of the document.
    """
    page_number: int
    image_path: str
    original_width: int
    original_height: int
    words: List[OCRWord] = Field(default_factory=list)
    regions: List[DocumentRegion] = Field(default_factory=list)


class DocumentRepresentation(BaseModel):
    """
    The final structured output from the V2 Document Intelligence pipeline.
    """
    document_id: str
    pages: List[PageRepresentation] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TemplateFingerprint(BaseModel):
    """
    A deterministic structural signature of a document's layout.
    """
    spatial_grid: List[float] = Field(default_factory=list) # 10x10 density grid flattened to 100
    x_alignment_hist: List[float] = Field(default_factory=list) # Histogram of left-x positions
    y_alignment_hist: List[float] = Field(default_factory=list) # Histogram of y positions (rows)
    region_centroids: Dict[str, list[float]] = Field(default_factory=dict) # str -> [x, y]
    whitespace_ratio: float = 0.0

class MatchResult(BaseModel):
    """
    Result of a scalable FAISS similarity search.
    """
    document_id: str
    matched_document_id: str
    similarity_score: float
    structural_similarity: float
    visual_similarity: float
    embedding_similarity: float
    confidence: float
