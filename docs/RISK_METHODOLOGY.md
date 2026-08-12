# Fraud Risk Scoring Methodology

MedExtract V2 implements a contextual Fraud Risk Engine that sits on top of the deterministic Structural Fingerprint FAISS similarity index.

## The Core Problem
High structural similarity **does not automatically equal fraud**. 

Legitimate clinics generate hundreds of documents daily using the exact same underlying template (e.g., an EHR-generated prescription or a standard Quickbooks invoice). If the system were to blindly flag any document with >0.95 similarity as "Fraud", the False Positive rate would be unacceptable in production.

## The Contextual Solution
The Risk Engine (`app/engine/risk_engine.py`) takes the raw similarity metrics and contextualizes them against business metadata (Claimed Provider, Patient Name, Invoice Amounts). 

It utilizes centralized scoring weights (`app/engine/risk_config.py`) to generate a 0-100 Risk Score, categorized into GREEN, AMBER, and RED levels.

### 1. Legitimate Template Reuse (GREEN)
- **Condition**: Structural Similarity > 0.95 + **Same** Provider + **Different** Patient/Date.
- **Interpretation**: This is standard business behavior. Clinic A submitted a valid claim for a new patient using their standard template.
- **Output**: Base Green Score (~5), "Legitimate Template Reuse".

### 2. Potential Fraudulent Reuse / Template Cloning (RED)
- **Condition**: Structural Similarity > 0.95 + **Different** Provider.
- **Interpretation**: A high-risk indicator. Scammer B has taken the legitimate invoice template of Provider A, changed the logo and text to say "Scam Clinic B", and submitted it. The structural FAISS index catches the stolen layout.
- **Output**: Base Red Score (80) + Penalty (40) = **100**. "Requires Investigation (Potential Fraudulent Reuse)".

### 3. Exact Duplicate Submission (AMBER / RED)
- **Condition**: Structural Similarity > 0.95 + **Same** Provider + **Same** Patient + **Same** Amount.
- **Interpretation**: A user submitted the exact same bill twice (either accidentally or intentionally double-dipping).
- **Output**: Base Amber Score (50) + Penalty (30) = **80**. "Requires Investigation (Duplicate Submission)".

### 4. Generic Template Usage (AMBER)
- **Condition**: Moderate Similarity (0.85 - 0.95) + **Different** Provider.
- **Interpretation**: Multiple legitimate providers might simply be using the default Microsoft Word invoice template. The structure is similar, but not pixel-perfect identical enough to guarantee cloning.
- **Output**: Base Amber Score (50). "Suspicious Similarity (Generic Template Usage)".

## Disclaimer Language
The algorithm is designed to assist human investigators, not replace them. The engine strictly avoids legally compromising language. It outputs phrases like `"Requires Investigation"`, `"Potential Fraud"`, and `"Suspicious Similarity"` rather than claiming definitive proof of illegal activity.
