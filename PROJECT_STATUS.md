# PROJECT STATUS: MedExtract (Controlled Final Alignment)

## Overview
MedExtract is a document template matching and fraud-risk intelligence system built for the problem statement: **"Similar Document Template Matching Algorithm"**.

The core objective is fully satisfied: the system deterministically identifies reimbursement claims that reuse the exact same underlying document template (margins, table geometry, header/footer structure), even when provider names, logos, patient information, dates, and amounts have been modified.

---

## Final UI Navigation Structure
- **Dashboard**: Real-time system metrics, total document counts, risk breakdown (Red/Amber/Green), processing volume line chart, and recent alert case feed.
- **Upload Documents**: Ingestion pipeline supporting PDF, PNG, and JPG uploads with background extraction and fingerprint indexing.
- **Provider Templates**: Registration of reference templates per healthcare provider category (`hospital`, `doctor`, `lab`) for automatic structural verification.
- **Investigation Queue**: Investigator-focused review queue listing flagged RED ("High Fraud Risk") and AMBER ("Suspicious Layout") documents with deletion capabilities.
- **Document Analysis**: Detailed document inspection showing extracted fields, raw OCR text, risk score, and provider verification status.
- **Similarity Search**: Side-by-side visual analysis exposing Template Similarity %, Structural Match evidence, and Content / Identity changes.

---

## Core Algorithm & Tech Stack
1. **Preprocessing & OCR**: OpenCV deskewing, resolution normalization, and Tesseract layout parsing.
2. **Structural Fingerprinting**: Content-invariant layout vectorization combining spatial grid distribution, x/y alignment histograms, and region centroids.
3. **Retrieval Engine**: Sub-millisecond FAISS vector similarity search (80% structural, 20% visual layout embedding).
4. **Contextual Fraud-Risk Engine**: Evaluates structural template similarity against provider registration to assign GREEN (Low Risk), AMBER (Suspicious Layout), or RED (High Fraud Risk).

---

## Risk Terminology & Interpretation
- 🟢 **GREEN (Low Risk)**: No suspicious template relationship detected; layout matches registered provider structure.
- 🟡 **AMBER (Suspicious Layout)**: Anomalous template similarity detected requiring investigator review.
- 🔴 **RED (High Fraud Risk)**: Strong evidence of suspicious template reuse across unverified provider identities requiring full investigation.

---

## Synthetic Benchmark Evaluation
Evaluation on the isolated synthetic dataset (`evaluate_fraud_accuracy.py` / `tests/test_end_to_end.py`) demonstrates:
- **Cloned / Reused Templates**: Structural similarity > 95% (FAISS distance < 0.1)
- **Distinct Templates**: Structural similarity < 60% (FAISS distance > 0.4)
- **Classification Accuracy**: High precision and recall on synthetic test pairs.

