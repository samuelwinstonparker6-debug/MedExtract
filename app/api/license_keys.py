import re
import random
import string
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.domain import LicenseKey

logger = logging.getLogger(__name__)

router = APIRouter()

# Format: AAaANN  (2 uppercase, 1 lowercase, 1 uppercase, 2 digits)
_KEY_PATTERN = re.compile(r'^[A-Z]{2}[a-z][A-Z]\d{2}$')


def _generate_unique_key(db: Session) -> str:
    """Generate a random AAaANN key that does not already exist in the DB."""
    for _ in range(100):
        upper1 = random.choices(string.ascii_uppercase, k=2)
        lower1 = random.choices(string.ascii_lowercase, k=1)
        upper2 = random.choices(string.ascii_uppercase, k=1)
        digits = random.choices(string.digits, k=2)
        key = "".join(upper1 + lower1 + upper2 + digits)
        exists = db.query(LicenseKey).filter(LicenseKey.license_key == key).first()
        if not exists:
            return key
    raise RuntimeError("Could not generate a unique license key after 100 attempts.")


def verify_license_key(db: Session, license_key: str, patient_name: str) -> dict:
    """
    Verifies a license key + patient name pair.

    Returns a dict:
        { "status": "REAL" | "FAKE", "reason": str }

    Checks (in order):
      1. Format must match AAaANN regex.
      2. Key must exist in the license_keys table.
      3. Key must be bonded to the given patient name (case-insensitive).
    """
    if not license_key or not patient_name:
        return {"status": "FAKE", "reason": "missing key or patient name"}

    # 1. Format validation
    if not _KEY_PATTERN.match(license_key):
        return {"status": "FAKE", "reason": "invalid key format (expected AAaANN e.g. XBz412)"}

    # 2. Existence check
    record = db.query(LicenseKey).filter(LicenseKey.license_key == license_key).first()
    if not record:
        return {"status": "FAKE", "reason": "key not found in database"}

    # 3. Name binding check (case-insensitive)
    if record.patient_name.strip().lower() != patient_name.strip().lower():
        return {
            "status": "FAKE",
            "reason": f"key is bonded to a different patient ('{record.patient_name}')"
        }

    return {"status": "REAL", "reason": "key and patient name match"}


# ── Pydantic schemas ───────────────────────────────────────────────────────────

class GenerateKeyRequest(BaseModel):
    patient_name: str


class VerifyKeyRequest(BaseModel):
    license_key: str
    patient_name: str


# ── API Endpoints ──────────────────────────────────────────────────────────────

@router.get("")
def list_license_keys(db: Session = Depends(get_db)):
    """Return all generated license keys (newest first)."""
    keys = db.query(LicenseKey).order_by(LicenseKey.id.desc()).all()
    return [
        {
            "id": k.id,
            "license_key": k.license_key,
            "patient_name": k.patient_name,
            "created_at": k.created_at,
        }
        for k in keys
    ]


@router.post("/generate")
def generate_license_key(request: GenerateKeyRequest, db: Session = Depends(get_db)):
    """
    Generate a unique AAaANN license key bonded to the given patient name.
    Saves the key-patient pair to the database and returns it.
    """
    patient_name = request.patient_name.strip()
    if not patient_name:
        raise HTTPException(status_code=400, detail="patient_name must not be empty")

    try:
        key = _generate_unique_key(db)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    record = LicenseKey(license_key=key, patient_name=patient_name)
    db.add(record)
    db.commit()
    db.refresh(record)

    logger.info("Generated license key '%s' for patient '%s'", key, patient_name)

    return {
        "id": record.id,
        "license_key": record.license_key,
        "patient_name": record.patient_name,
        "created_at": record.created_at,
    }


@router.post("/verify")
def verify_key_endpoint(request: VerifyKeyRequest, db: Session = Depends(get_db)):
    """
    Verify whether a license key is REAL or FAKE based on format, existence,
    and name-binding checks.
    """
    result = verify_license_key(db, request.license_key, request.patient_name)
    return result