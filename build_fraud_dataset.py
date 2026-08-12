"""
build_fraud_dataset.py
----------------------
Generates a comprehensive labeled fraud dataset in tests/fraud_dataset/ covering:
  - Invoice documents        (3 genuine pairs + 3 fraud pairs)
  - Prescription documents   (3 genuine pairs + 3 fraud pairs)
  - Lab Report documents     (3 genuine pairs + 3 fraud pairs)

Total: 18 pairs (9 genuine, 9 fraud) across 3 document types.

Output structure
----------------
tests/fraud_dataset/
    invoices/
        inv_genuine1_a.png  inv_genuine1_b.png  ...
    prescriptions/
        presc_genuine1_a.png  ...
    lab_reports/
        lab_genuine1_a.png  ...
    labels.json     <- consumed by evaluate_fraud_accuracy.py

labels.json schema (matches evaluate_fraud_accuracy.py expectations)
----------------------------------------------------------------------
{
  "entries": [
    {
      "pair":        ["invoices/inv_genuine1_a.png", "invoices/inv_genuine1_b.png"],
      "label":       "genuine",           // "genuine" | "fraud"
      "doc_type":    "invoice",           // "invoice" | "prescription" | "lab_report"
      "description": "Human-readable note"
    },
    ...
  ]
}

Usage
-----
    python build_fraud_dataset.py
"""

import cv2
import numpy as np
import os
import json

OUTPUT_DIR = "tests/fraud_dataset"
FONT = cv2.FONT_HERSHEY_SIMPLEX


# ─────────────────────────────────────────────────────────────
# Document-image generators
# ─────────────────────────────────────────────────────────────

def draw_invoice(provider: str, patient: str, amount: str, date: str,
                 bg_color=(255, 255, 255)) -> np.ndarray:
    """Renders an 800x1050 invoice image using OpenCV."""
    img = np.ones((1050, 800, 3), dtype=np.uint8)
    img[:] = bg_color

    # Header bar
    cv2.rectangle(img, (0, 0), (800, 90), (30, 80, 160), -1)
    cv2.putText(img, "MEDICAL INVOICE", (210, 60), FONT, 1.3, (255, 255, 255), 2)

    # Provider box
    cv2.rectangle(img, (40, 110), (380, 230), (60, 60, 60), 2)
    cv2.putText(img, "PROVIDER", (55, 140), FONT, 0.6, (80, 80, 80), 1)
    cv2.putText(img, provider[:28], (55, 185), FONT, 0.85, (0, 0, 0), 2)

    # Patient box
    cv2.rectangle(img, (420, 110), (760, 230), (60, 60, 60), 2)
    cv2.putText(img, "PATIENT", (435, 140), FONT, 0.6, (80, 80, 80), 1)
    cv2.putText(img, patient[:28], (435, 185), FONT, 0.85, (0, 0, 0), 2)

    # Date + Invoice No
    cv2.putText(img, f"Invoice Date: {date}", (40, 270), FONT, 0.7, (0, 0, 0), 1)
    cv2.putText(img, f"Invoice No: INV-{date.replace('-','')[:8]}", (450, 270), FONT, 0.65, (80, 80, 80), 1)

    # Table header
    cv2.line(img, (40, 310), (760, 310), (0, 0, 0), 2)
    cv2.putText(img, "Description", (50, 340), FONT, 0.75, (0, 0, 0), 1)
    cv2.putText(img, "Qty", (470, 340), FONT, 0.75, (0, 0, 0), 1)
    cv2.putText(img, "Amount", (600, 340), FONT, 0.75, (0, 0, 0), 1)
    cv2.line(img, (40, 358), (760, 358), (0, 0, 0), 2)

    # Table rows
    rows = [
        ("Consultation Fee", "1", "Rs.800"),
        ("Lab Tests (CBC)", "1", "Rs.450"),
        ("Medicines", "3", "Rs.320"),
        ("X-Ray", "1", "Rs.600"),
    ]
    for i, (desc, qty, amt) in enumerate(rows):
        y = 395 + i * 48
        cv2.putText(img, desc, (50, y), FONT, 0.72, (0, 0, 0), 1)
        cv2.putText(img, qty, (480, y), FONT, 0.72, (0, 0, 0), 1)
        cv2.putText(img, amt, (600, y), FONT, 0.72, (0, 0, 0), 1)

    # Total box
    cv2.line(img, (40, 600), (760, 600), (0, 0, 0), 2)
    cv2.rectangle(img, (490, 615), (760, 660), (220, 235, 255), -1)
    cv2.putText(img, f"TOTAL: {amount}", (505, 648), FONT, 0.95, (0, 0, 130), 2)

    # Footer
    cv2.putText(img, "Authorized Signature: ___________________",
                (40, 950), FONT, 0.6, (100, 100, 100), 1)
    cv2.putText(img, "Thank you for choosing our services.",
                (230, 1010), FONT, 0.6, (130, 130, 130), 1)
    return img


def draw_prescription(doctor: str, patient: str, date: str,
                       medicines: list, diagnosis: str,
                       bg_color=(255, 255, 252)) -> np.ndarray:
    """Renders an 800x1050 prescription image using OpenCV."""
    img = np.ones((1050, 800, 3), dtype=np.uint8)
    img[:] = bg_color

    # Header
    cv2.rectangle(img, (0, 0), (800, 100), (20, 120, 80), -1)
    cv2.putText(img, "PRESCRIPTION", (255, 65), FONT, 1.3, (255, 255, 255), 2)

    # Doctor info box
    cv2.rectangle(img, (40, 120), (760, 215), (220, 240, 220), -1)
    cv2.putText(img, f"Dr. {doctor}", (55, 160), FONT, 0.9, (0, 80, 40), 2)
    cv2.putText(img, "MBBS, MD  |  Reg. No: MH-2021-09876",
                (55, 200), FONT, 0.55, (60, 80, 60), 1)

    # Patient & date
    cv2.putText(img, f"Patient: {patient}", (40, 260), FONT, 0.8, (0, 0, 0), 1)
    cv2.putText(img, f"Date: {date}", (530, 260), FONT, 0.75, (0, 0, 0), 1)

    # Diagnosis row
    cv2.rectangle(img, (40, 285), (760, 325), (245, 245, 200), -1)
    cv2.putText(img, f"Diagnosis: {diagnosis}", (50, 315), FONT, 0.72, (0, 0, 0), 1)

    # Rx heading
    cv2.putText(img, "Rx", (40, 380), FONT, 1.8, (0, 100, 50), 2)
    cv2.line(img, (40, 395), (760, 395), (0, 140, 70), 2)

    # Medicines
    for i, med in enumerate(medicines[:5]):
        y = 440 + i * 60
        cv2.putText(img, f"{i+1}.  {med}", (60, y), FONT, 0.75, (0, 0, 0), 1)
        cv2.putText(img, "Twice daily after meals x 5 days",
                    (90, y + 25), FONT, 0.55, (90, 90, 90), 1)

    # Signature
    cv2.putText(img, "Doctor's Signature: ___________________",
                (40, 950), FONT, 0.65, (100, 100, 100), 1)
    cv2.putText(img, "Follow up in 7 days.",
                (40, 1010), FONT, 0.6, (130, 130, 130), 1)
    return img


def draw_lab_report(lab_name: str, patient: str, date: str,
                    tests: list, bg_color=(255, 255, 255)) -> np.ndarray:
    """Renders an 800x1050 lab report image using OpenCV."""
    img = np.ones((1050, 800, 3), dtype=np.uint8)
    img[:] = bg_color

    # Header
    cv2.rectangle(img, (0, 0), (800, 100), (100, 30, 160), -1)
    cv2.putText(img, "LABORATORY REPORT", (180, 65), FONT, 1.2, (255, 255, 255), 2)

    # Lab name box
    cv2.rectangle(img, (40, 115), (760, 185), (230, 215, 255), -1)
    cv2.putText(img, lab_name[:36], (55, 162), FONT, 0.85, (60, 0, 120), 2)

    # Patient & date
    cv2.putText(img, f"Patient Name: {patient}", (40, 225), FONT, 0.78, (0, 0, 0), 1)
    cv2.putText(img, f"Report Date: {date}", (450, 225), FONT, 0.72, (0, 0, 0), 1)
    cv2.putText(img, f"Sample ID: LAB{date.replace('-','')[:8]}",
                (40, 260), FONT, 0.65, (80, 80, 80), 1)

    # Table header
    cv2.line(img, (40, 290), (760, 290), (0, 0, 0), 2)
    cv2.putText(img, "Test Name", (50, 320), FONT, 0.72, (0, 0, 0), 1)
    cv2.putText(img, "Result", (380, 320), FONT, 0.72, (0, 0, 0), 1)
    cv2.putText(img, "Ref. Range", (530, 320), FONT, 0.72, (0, 0, 0), 1)
    cv2.putText(img, "Status", (690, 320), FONT, 0.72, (0, 0, 0), 1)
    cv2.line(img, (40, 338), (760, 338), (0, 0, 0), 2)

    # Test rows
    for i, (name, result, ref, status) in enumerate(tests[:7]):
        y = 375 + i * 50
        color = (180, 0, 0) if status in ("HIGH", "LOW") else (0, 0, 0)
        cv2.putText(img, name,   (50, y),  FONT, 0.68, (0, 0, 0), 1)
        cv2.putText(img, result, (390, y), FONT, 0.68, color, 1)
        cv2.putText(img, ref,    (535, y), FONT, 0.65, (80, 80, 80), 1)
        cv2.putText(img, status, (695, y), FONT, 0.65, color, 1)

    # Pathologist line
    cv2.line(img, (40, 900), (760, 900), (0, 0, 0), 1)
    cv2.putText(img, "Pathologist Signature: ___________________",
                (40, 940), FONT, 0.65, (100, 100, 100), 1)
    cv2.putText(img, "Report verified and digitally sealed.",
                (220, 1010), FONT, 0.6, (130, 130, 130), 1)
    return img


# ─────────────────────────────────────────────────────────────
# Main dataset builder
# ─────────────────────────────────────────────────────────────

def main():
    os.makedirs(f"{OUTPUT_DIR}/invoices",      exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/prescriptions", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/lab_reports",   exist_ok=True)

    # entries list — matches evaluate_fraud_accuracy.py schema
    # {"pair": [relPathA, relPathB], "label": "genuine"|"fraud",
    #  "doc_type": "...", "description": "..."}
    entries = []

    def save(rel_path: str, img: np.ndarray):
        cv2.imwrite(f"{OUTPUT_DIR}/{rel_path}", img)

    def add(pair_a, pair_b, label, doc_type, description, provider_a="", provider_b=""):
        entries.append({
            "pair": [pair_a, pair_b],
            "label": label,
            "doc_type": doc_type,
            "description": description,
            "provider_a": provider_a,
            "provider_b": provider_b,
        })

    # ── Shared test data ──────────────────────────────────────
    meds_a = ["Amoxicillin 500mg", "Paracetamol 650mg", "Cetirizine 10mg", "Omeprazole 20mg"]
    meds_b = ["Azithromycin 250mg", "Ibuprofen 400mg", "Loratadine 10mg", "Pantoprazole 40mg"]

    tests_normal = [
        ("Hemoglobin",    "13.5 g/dL",  "12.0-17.5",    "NORMAL"),
        ("WBC Count",     "7200 /uL",   "4000-11000",    "NORMAL"),
        ("Platelet Count","215000 /uL", "150000-400000", "NORMAL"),
        ("Blood Glucose", "92 mg/dL",   "70-110",        "NORMAL"),
        ("Creatinine",    "0.9 mg/dL",  "0.6-1.2",       "NORMAL"),
    ]
    tests_abnormal = [
        ("Hemoglobin",    "8.2 g/dL",   "12.0-17.5",    "LOW"),
        ("WBC Count",     "14500 /uL",  "4000-11000",    "HIGH"),
        ("Platelet Count","98000 /uL",  "150000-400000", "LOW"),
        ("Blood Glucose", "187 mg/dL",  "70-110",        "HIGH"),
        ("HbA1c",         "8.1%",       "< 5.7%",        "HIGH"),
    ]

    # ===========================================================
    # INVOICES
    # ===========================================================
    print("Generating Invoice samples...")

    # --- Genuine pairs ---
    # G1: Same provider, different patients (legitimate template reuse)
    save("invoices/inv_genuine1_a.png",
         draw_invoice("Apollo Hospitals", "Ramesh Kumar", "Rs.2170", "2024-01-15"))
    save("invoices/inv_genuine1_b.png",
         draw_invoice("Apollo Hospitals", "Sita Devi",   "Rs.1950", "2024-01-22"))
    add("invoices/inv_genuine1_a.png", "invoices/inv_genuine1_b.png",
        "genuine", "invoice",
        "Apollo Hospitals: two patients, same template — should score NONE",
        provider_a="Apollo Hospitals", provider_b="Apollo Hospitals")

    # G2: Completely different providers & layouts (no template overlap)
    save("invoices/inv_genuine2_a.png",
         draw_invoice("City Medical Centre", "Priya Sharma", "Rs.3800", "2024-02-10",
                      bg_color=(250, 255, 250)))
    save("invoices/inv_genuine2_b.png",
         draw_invoice("Rainbow Clinic", "Anil Mehta", "Rs.1200", "2024-02-18",
                      bg_color=(255, 250, 250)))
    add("invoices/inv_genuine2_a.png", "invoices/inv_genuine2_b.png",
        "genuine", "invoice",
        "Different providers, different layouts — no fraud signal expected",
        provider_a="City Medical Centre", provider_b="Rainbow Clinic")

    # G3: Same provider chain
    save("invoices/inv_genuine3_a.png",
         draw_invoice("Fortis Healthcare", "Mohan Das",   "Rs.4500", "2024-03-01"))
    save("invoices/inv_genuine3_b.png",
         draw_invoice("Fortis Healthcare", "Lakshmi Bai", "Rs.3200", "2024-03-12"))
    add("invoices/inv_genuine3_a.png", "invoices/inv_genuine3_b.png",
        "genuine", "invoice",
        "Fortis Healthcare: same provider chain, two patients — genuine",
        provider_a="Fortis Healthcare", provider_b="Fortis Healthcare")

    # --- Fraud pairs ---
    # F1: AMBER — Near-identical layout, only patient name differs, providers seen as different
    save("invoices/inv_fraud1_a.png",
         draw_invoice("Apollo Hospitals", "Ramesh Kumar", "Rs.2170", "2024-01-15"))
    save("invoices/inv_fraud1_b.png",
         draw_invoice("Apollo Hospitals", "Raj Kumar",    "Rs.2170", "2024-01-15"))
    add("invoices/inv_fraud1_a.png", "invoices/inv_fraud1_b.png",
        "fraud", "invoice",
        "Near-identical invoice — only patient name changed — possible photoshop fraud",
        provider_a="Apollo Hospitals", provider_b="Fraudulent Provider")

    # F2: RED — Same template structure but provider name swapped (template reuse forgery)
    save("invoices/inv_fraud2_a.png",
         draw_invoice("Apollo Hospitals",  "Ramesh Kumar", "Rs.2170", "2024-01-15"))
    save("invoices/inv_fraud2_b.png",
         draw_invoice("Fraudulent Clinic", "Ramesh Kumar", "Rs.2170", "2024-01-15"))
    add("invoices/inv_fraud2_a.png", "invoices/inv_fraud2_b.png",
        "fraud", "invoice",
        "Apollo template reused by Fraudulent Clinic — RED template-reuse forgery",
        provider_a="Apollo Hospitals", provider_b="Fraudulent Clinic")

    # F3: RED — Clone of known template used by unregistered entity
    save("invoices/inv_fraud3_a.png",
         draw_invoice("Apollo Hospitals", "Geeta Pillai", "Rs.5000", "2024-04-01"))
    save("invoices/inv_fraud3_b.png",
         draw_invoice("Fake Medcare",     "Geeta Pillai", "Rs.5000", "2024-04-01"))
    add("invoices/inv_fraud3_a.png", "invoices/inv_fraud3_b.png",
        "fraud", "invoice",
        "Apollo Hospitals template cloned by Fake Medcare — RED forgery",
        provider_a="Apollo Hospitals", provider_b="Fake Medcare")

    inv_count = len(entries)
    print(f"  Generated {inv_count} invoice pairs")

    # ===========================================================
    # PRESCRIPTIONS
    # ===========================================================
    print("Generating Prescription samples...")
    presc_start = len(entries)

    # G1: Same doctor, different patients
    save("prescriptions/presc_genuine1_a.png",
         draw_prescription("Suresh Verma", "Anita Roy",  "2024-01-20", meds_a, "Acute Pharyngitis"))
    save("prescriptions/presc_genuine1_b.png",
         draw_prescription("Suresh Verma", "Ravi Singh", "2024-01-28", meds_b, "Seasonal Allergy"))
    add("prescriptions/presc_genuine1_a.png", "prescriptions/presc_genuine1_b.png",
        "genuine", "prescription",
        "Dr. Suresh Verma: two different patients — legitimate reuse",
        provider_a="Dr. Suresh Verma", provider_b="Dr. Suresh Verma")

    # G2: Different doctors, different medications
    save("prescriptions/presc_genuine2_a.png",
         draw_prescription("Meena Kapoor", "Sunil Joshi",  "2024-02-05", meds_a, "URTI"))
    save("prescriptions/presc_genuine2_b.png",
         draw_prescription("Arjun Nair",   "Pooja Menon",  "2024-02-14", meds_b, "Migraine"))
    add("prescriptions/presc_genuine2_a.png", "prescriptions/presc_genuine2_b.png",
        "genuine", "prescription",
        "Different doctors prescribing different medications — no fraud",
        provider_a="Dr. Meena Kapoor", provider_b="Dr. Arjun Nair")

    # G3: Same doctor, different diagnoses
    save("prescriptions/presc_genuine3_a.png",
         draw_prescription("Pradeep Kumar", "Vandana Shah", "2024-03-08", meds_b, "Type 2 Diabetes"))
    save("prescriptions/presc_genuine3_b.png",
         draw_prescription("Pradeep Kumar", "Kiran Bedi",   "2024-03-15", meds_a, "Hypertension"))
    add("prescriptions/presc_genuine3_a.png", "prescriptions/presc_genuine3_b.png",
        "genuine", "prescription",
        "Dr. Pradeep Kumar: different patients with different diagnoses — genuine",
        provider_a="Dr. Pradeep Kumar", provider_b="Dr. Pradeep Kumar")

    # F1: RED — Doctor name swapped on cloned prescription template
    save("prescriptions/presc_fraud1_a.png",
         draw_prescription("Suresh Verma",    "Anita Roy", "2024-01-20", meds_a, "Acute Pharyngitis"))
    save("prescriptions/presc_fraud1_b.png",
         draw_prescription("Fake Doctor Raj", "Anita Roy", "2024-01-20", meds_a, "Acute Pharyngitis"))
    add("prescriptions/presc_fraud1_a.png", "prescriptions/presc_fraud1_b.png",
        "fraud", "prescription",
        "Dr. Suresh Verma prescription cloned with Fake Doctor name — RED forgery",
        provider_a="Dr. Suresh Verma", provider_b="Dr. Fake Doctor Raj")

    # F2: AMBER — Near-pixel-perfect, only patient name changed
    save("prescriptions/presc_fraud2_a.png",
         draw_prescription("Meena Kapoor", "Sunil Joshi",   "2024-02-05", meds_a, "URTI"))
    save("prescriptions/presc_fraud2_b.png",
         draw_prescription("Meena Kapoor", "Fake Patient",  "2024-02-05", meds_a, "URTI"))
    add("prescriptions/presc_fraud2_a.png", "prescriptions/presc_fraud2_b.png",
        "fraud", "prescription",
        "Identical prescription, only patient name changed — possible AMBER photoshop fraud",
        provider_a="Dr. Meena Kapoor", provider_b="Dr. Imposter")

    # F3: RED — Template wholesale reuse by unregistered entity
    save("prescriptions/presc_fraud3_a.png",
         draw_prescription("Pradeep Kumar", "Vandana Shah",  "2024-03-08", meds_b, "Type 2 Diabetes"))
    save("prescriptions/presc_fraud3_b.png",
         draw_prescription("Ghost Clinic Dr","Vandana Shah", "2024-03-08", meds_b, "Type 2 Diabetes"))
    add("prescriptions/presc_fraud3_a.png", "prescriptions/presc_fraud3_b.png",
        "fraud", "prescription",
        "Dr. Pradeep Kumar template used by Ghost Clinic — RED template-reuse fraud",
        provider_a="Dr. Pradeep Kumar", provider_b="Dr. Ghost Clinic")

    print(f"  Generated {len(entries) - presc_start} prescription pairs")

    # ===========================================================
    # LAB REPORTS
    # ===========================================================
    print("Generating Lab Report samples...")
    lab_start = len(entries)

    # G1: Same lab, different patients
    save("lab_reports/lab_genuine1_a.png",
         draw_lab_report("Metropolis Healthcare Lab", "Arvind Saxena", "2024-01-10", tests_normal))
    save("lab_reports/lab_genuine1_b.png",
         draw_lab_report("Metropolis Healthcare Lab", "Sunita Rao",    "2024-01-18", tests_abnormal))
    add("lab_reports/lab_genuine1_a.png", "lab_reports/lab_genuine1_b.png",
        "genuine", "lab_report",
        "Metropolis Lab: two patients, different results — genuine reports",
        provider_a="Metropolis Healthcare Lab", provider_b="Metropolis Healthcare Lab")

    # G2: Different labs
    save("lab_reports/lab_genuine2_a.png",
         draw_lab_report("SRL Diagnostics", "Harish Patel", "2024-02-02", tests_normal,
                         bg_color=(255, 252, 250)))
    save("lab_reports/lab_genuine2_b.png",
         draw_lab_report("Thyrocare Labs",  "Uma Krishnan", "2024-02-11", tests_normal,
                         bg_color=(252, 255, 252)))
    add("lab_reports/lab_genuine2_a.png", "lab_reports/lab_genuine2_b.png",
        "genuine", "lab_report",
        "Different labs, same test panel — no fraud expected",
        provider_a="SRL Diagnostics", provider_b="Thyrocare Labs")

    # G3: Same lab, different result sets
    save("lab_reports/lab_genuine3_a.png",
         draw_lab_report("Lal PathLabs", "Deepak Verma", "2024-03-05", tests_abnormal))
    save("lab_reports/lab_genuine3_b.png",
         draw_lab_report("Lal PathLabs", "Neha Gupta",   "2024-03-14", tests_normal))
    add("lab_reports/lab_genuine3_a.png", "lab_reports/lab_genuine3_b.png",
        "genuine", "lab_report",
        "Lal PathLabs: same lab, different patients and results — genuine",
        provider_a="Lal PathLabs", provider_b="Lal PathLabs")

    # F1: RED — Lab name swapped on otherwise identical report
    save("lab_reports/lab_fraud1_a.png",
         draw_lab_report("Metropolis Healthcare Lab", "Arvind Saxena", "2024-01-10", tests_normal))
    save("lab_reports/lab_fraud1_b.png",
         draw_lab_report("Bogus Diagnostics Co",      "Arvind Saxena", "2024-01-10", tests_normal))
    add("lab_reports/lab_fraud1_a.png", "lab_reports/lab_fraud1_b.png",
        "fraud", "lab_report",
        "Metropolis template used by Bogus Diagnostics — RED lab report forgery",
        provider_a="Metropolis Healthcare Lab", provider_b="Bogus Diagnostics Co")

    # F2: AMBER — Patient name altered on near-identical report
    save("lab_reports/lab_fraud2_a.png",
         draw_lab_report("SRL Diagnostics", "Harish Patel",   "2024-02-02", tests_normal))
    save("lab_reports/lab_fraud2_b.png",
         draw_lab_report("SRL Diagnostics", "Imposter Name",  "2024-02-02", tests_normal))
    add("lab_reports/lab_fraud2_a.png", "lab_reports/lab_fraud2_b.png",
        "fraud", "lab_report",
        "SRL Diagnostics: patient name swapped — possible AMBER photoshop fraud",
        provider_a="SRL Diagnostics", provider_b="Fake SRL Copy")

    # F3: RED — Template reuse by unregistered entity
    save("lab_reports/lab_fraud3_a.png",
         draw_lab_report("Lal PathLabs", "Deepak Verma",  "2024-03-05", tests_abnormal))
    save("lab_reports/lab_fraud3_b.png",
         draw_lab_report("Shady Labs Inc.", "Deepak Verma","2024-03-05", tests_abnormal))
    add("lab_reports/lab_fraud3_a.png", "lab_reports/lab_fraud3_b.png",
        "fraud", "lab_report",
        "Lal PathLabs template used by Shady Labs Inc. — RED template-reuse forgery",
        provider_a="Lal PathLabs", provider_b="Shady Labs Inc.")

    print(f"  Generated {len(entries) - lab_start} lab report pairs")

    # ── Write labels.json ─────────────────────────────────────
    labels_path = f"{OUTPUT_DIR}/labels.json"
    with open(labels_path, "w") as f:
        json.dump({"entries": entries}, f, indent=2)

    genuine_count = sum(1 for e in entries if e["label"] == "genuine")
    fraud_count   = sum(1 for e in entries if e["label"] == "fraud")

    print(f"\n[OK] Dataset generated: {len(entries)} total pairs "
          f"({genuine_count} genuine, {fraud_count} fraud)")
    print(f"   Labels written to: {labels_path}")
    print(f"   Output directory : {OUTPUT_DIR}/")
    print("\nNext step:")
    print("  python evaluate_fraud_accuracy.py")


if __name__ == "__main__":
    main()
