from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class DocumentResponse(BaseModel):
    """
    Public representation of a Document record.
    IMPORTANT: file_path is intentionally excluded — it is a server-side
    implementation detail and must never be sent to clients.
    Use the filename field to derive the public URL: /uploads/{filename}
    """
    model_config = {'from_attributes': True}

    id: int
    filename: Optional[str] = None
    upload_timestamp: Optional[datetime] = None
    source_type: Optional[str] = 'unknown'
    status: Optional[str] = 'pending'
    document_type: Optional[str] = None
    structured_data: Optional[dict] = None
    layout_features: Optional[Any] = None
    fingerprint_version: Optional[int] = 2
    fraud_status: Optional[str] = 'NONE'
    fraud_score: Optional[float] = 0.0
    fraud_flags: Optional[list] = None
    reference_verification_result: Optional[str] = None


class ProviderReferenceResponse(BaseModel):
    """Public representation of a ProviderReference record."""
    model_config = {'from_attributes': True}

    id: int
    category: str
    label: str
    fingerprint_version: Optional[int] = 2
    date_registered: Optional[datetime] = None
