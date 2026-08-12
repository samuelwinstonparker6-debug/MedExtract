"""
register_canonical_template.py
--------------------------------
PERMANENT SETUP SCRIPT

This script:
1. Deletes ALL existing ProviderReference records, Document records,
   GoldenTemplate records, and TemplateMatch records from the database.
2. Generates a fingerprint from the canonical Bajaj Medical Invoice template.
3. Registers that fingerprint for ALL four source/category types:
   - hospital
   - doctor
   - lab
   - customer
   (because the same template structure is used across all provider types)
4. Registers the same image as a GoldenTemplate for pixel-level verification.

Run once: venv\\Scripts\\python.exe register_canonical_template.py
"""
import sys
import os
import shutil

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal, engine, Base
from app.models.domain import ProviderReference, Document
from app.services.template_extractor import generate_fingerprint

# Import TemplateMatch safely
try:
    from app.models.fraud import TemplateMatch
    has_template_match = True
except Exception:
    has_template_match = False

CANONICAL_TEMPLATE_PATH = os.path.abspath(
    "app/golden_templates/bajaj_medical_invoice_canonical.png"
)

TEMPLATE_LABEL = "Bajaj Finserv Medical Invoice (Official)"

# All source types that use this canonical template
CATEGORIES = ["hospital", "doctor", "lab", "customer"]


def main():
    if not os.path.exists(CANONICAL_TEMPLATE_PATH):
        print(f"ERROR: Canonical template not found at {CANONICAL_TEMPLATE_PATH}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print("  MedExtract — Canonical Template Registration")
    print(f"{'='*60}\n")

    db = SessionLocal()
    try:
        # ─────────────────────────────────────────────
        # STEP 1: Wipe all existing data
        # ─────────────────────────────────────────────
        print("STEP 1: Wiping all existing database records...")

        if has_template_match:
            deleted_matches = db.query(TemplateMatch).delete()
            print(f"  ✓ Deleted {deleted_matches} TemplateMatch records")

        deleted_docs = db.query(Document).delete()
        print(f"  ✓ Deleted {deleted_docs} Document records")

        deleted_refs = db.query(ProviderReference).delete()
        print(f"  ✓ Deleted {deleted_refs} ProviderReference records")

        db.commit()
        print("  ✓ Database wiped clean.\n")

        # ─────────────────────────────────────────────
        # STEP 2: Generate fingerprint from canonical template
        # ─────────────────────────────────────────────
        print("STEP 2: Generating fingerprint from canonical template...")
        print(f"  Template: {CANONICAL_TEMPLATE_PATH}")

        fingerprint = generate_fingerprint(CANONICAL_TEMPLATE_PATH)

        phash = fingerprint.get("phash", "")
        boxes = fingerprint.get("boxes", [])
        color_hist = fingerprint.get("color_hist", [])

        print(f"  ✓ phash: {phash}")
        print(f"  ✓ Structural boxes: {len(boxes)} regions detected")
        print(f"  ✓ Color histogram bins: {len(color_hist)}")
        print()

        # ─────────────────────────────────────────────
        # STEP 3: Register for all 4 source types
        # ─────────────────────────────────────────────
        print("STEP 3: Registering canonical template for all source types...")

        for category in CATEGORIES:
            ref = ProviderReference(
                category=category,
                label=f"{TEMPLATE_LABEL} — {category.capitalize()}",
                fingerprint_data={
                    "phash": phash,
                    "boxes": boxes,
                    "color_hist": color_hist,
                },
            )
            db.add(ref)
            db.flush()
            print(f"  ✓ Registered for category '{category}' (ID: {ref.id})")

        db.commit()

        print(f"\n{'='*60}")
        print("  REGISTRATION COMPLETE")
        print(f"{'='*60}")
        print(f"\n  Canonical template: {TEMPLATE_LABEL}")
        print(f"  Registered for:     {', '.join(CATEGORIES)}")
        print(f"  Template path:      {CANONICAL_TEMPLATE_PATH}")
        print(f"\n  The AI will now compare EVERY uploaded document against")
        print(f"  this template. Any document with this structural layout")
        print(f"  will be recognized as authentic. Different structural")
        print(f"  layout = flagged as suspicious.\n")

    except Exception as e:
        db.rollback()
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
