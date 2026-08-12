from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, SmallInteger
from sqlalchemy.sql import func
from app.core.database import Base


class Document(Base):
    """
    Central record for every uploaded medical document.

    Status lifecycle: pending → extracted → completed | failed
    Fraud status: NONE | AMBER | RED
    """
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    source_type = Column(String, nullable=False)          # doctor | hospital | lab
    status = Column(String, default='pending')            # pending | extracted | completed | failed
    file_path = Column(String)                            # server-side only — never exposed to clients
    file_hash = Column(String, index=True, nullable=True) # SHA-256 for caching
    extracted_text = Column(String, nullable=True)
    document_type = Column(String, nullable=True)         # invoice | prescription | lab_report | other
    structured_data = Column(JSON, nullable=True)
    layout_features = Column(JSON, nullable=True)         # {phash, zone_boxes, zone_color_hist, aspect_ratio}
    fingerprint_version = Column(SmallInteger, default=2) # fingerprint algorithm version
    fraud_status = Column(String, default='NONE')         # NONE | AMBER | RED
    fraud_score = Column(Float, nullable=True)
    fraud_flags = Column(JSON, nullable=True)
    reference_verification_result = Column(String, nullable=True)
    completed_timestamp = Column(DateTime(timezone=True), nullable=True)


class ProviderReference(Base):
    """
    Golden-reference fingerprint for a known legitimate provider document.
    Used by the fraud pipeline for similarity comparison (Layer 3).
    """
    __tablename__ = 'provider_references'

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)         # hospital | doctor | lab
    label = Column(String, index=True)            # human-readable provider name
    fingerprint_data = Column(JSON)               # {phash, zone_boxes, zone_color_hist, aspect_ratio}
    fingerprint_version = Column(SmallInteger, default=2)
    date_registered = Column(DateTime(timezone=True), server_default=func.now())


class LicenseKey(Base):
    """
    Isolated demo feature for patient-facing access.
    NOT used by the fraud detection pipeline.
    """
    __tablename__ = 'license_keys'

    id = Column(Integer, primary_key=True, index=True)
    license_key = Column(String(6), unique=True, index=True, nullable=False)
    patient_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
