# IEEE Final-Year Project: Similar Document Template Matching for Fraud Detection

## Project Title
MedExtract: Structural Template Fingerprinting and Fraud Detection for Medical Invoices, Prescriptions, and Lab Reports

## Problem Statement
Fraudulent claimants often reuse the same printed or digital medical document template and only change small details such as provider names, logos, colors, or patient information. Traditional text-based comparison methods fail because the visible text is modified while the underlying layout remains the same.

## Solution Overview
MedExtract addresses this by extracting the structural fingerprint of a document and comparing the underlying layout rather than the OCR text. The system:
- extracts a structural template fingerprint from uploaded documents
- compares templates using similarity scoring
- flags suspicious or fraudulent reuse when the layout is highly similar but the provider context differs
- provides a color-coded investigation workflow for investigators

## Core Modules
1. Template Extraction
   - preprocesses uploaded documents
   - detects layout regions and structural anchors
   - builds a normalized structural fingerprint
2. Similarity Matching
   - compares fingerprints using cosine similarity and structural distance measures
   - indexes templates for fast retrieval
3. Fraud Risk Evaluation
   - analyzes structural similarity versus claimed provider metadata
   - assigns green, amber, or red risk levels
4. Demo and Evaluation
   - generates sample documents and reference templates
   - supports verification of genuine vs tampered template reuse

## Demo Workflow
1. Generate sample original and tampered documents.
2. Register the original provider template.
3. Upload a similar document and observe the similarity score.
4. Upload a tampered or mismatched provider document and observe the fraud flag.

## Evaluation Criteria
- accuracy of template matching
- ability to detect layout-based cloning
- robustness to minor text changes and formatting variations
- scalability to multiple provider templates
- explainability through risk evidence and visual comparison

## Expected Outcome
The project demonstrates that structural template fingerprinting can identify suspicious or fraudulent documents even when the visible text has been altered.
