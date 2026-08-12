"""
Centralized Configuration for the Fraud Risk Engine.

CONCEPTUAL HIERARCHY:
1. Template Similarity (0.0 to 1.0):
   - Measures structural layout resemblance (spatial grid, x/y alignment histograms, region bounding boxes).
   - Higher values (>0.85/0.95) indicate identical layout structure regardless of text content changes.

2. Contextual Fraud Risk Score (0 to 100):
   - Combines structural template similarity with contextual business logic:
     * Provider verification (does claimed provider own the template?)
     * Content variations (differing logos/licenses on cloned templates)
   - Final risk classification:
     * GREEN (0-49): Low Risk / Verified Template Usage
     * AMBER (50-79): Suspicious Layout / Anomalous Template Usage
     * RED (80-100): High Fraud Risk / Template Reuse Flagged for Investigation
"""

# Structural Similarity Thresholds (Layout Resemblance)
SIM_THRESH_EXACT = 0.98        # Essentially mathematically identical layout
SIM_THRESH_HIGH = 0.95         # High probability it's the exact same template
SIM_THRESH_SUSPICIOUS = 0.85   # Standardized template usage (e.g. generic Quickbooks invoice)
SIM_THRESH_RELATED = 0.70      # May share components but structurally distinct

# Visual Similarity Thresholds (Supporting Image Feature Vector)
VISUAL_THRESH_HIGH = 0.90      # Pixel-level similarity indicates direct cloning/photocopying
VISUAL_THRESH_LOW = 0.50       # Low visual similarity despite high structural suggests generic template use

# Base Scoring Weights (0-100 scale)
SCORE_BASE_GREEN = 5
SCORE_BASE_AMBER = 50
SCORE_BASE_RED = 80

# Specific Penalty Adjustments
PENALTY_DIFFERENT_PROVIDER = 40  # Massive penalty if structure is identical but claimed provider differs
PENALTY_EXACT_DUPLICATE = 30     # Same structure, provider, patient, and amount -> likely a duplicate submission mistake or double-dipping

# Evidence Language Mappings
EVIDENCE_SAME_STRUCT = "Highly identical document layout/structure"
EVIDENCE_SAME_VISUAL = "High pixel-level/visual similarity"
EVIDENCE_DIFF_PROVIDER = "Claimed provider name differs from known template owner"
EVIDENCE_SAME_PROVIDER = "Provider matches known template"
EVIDENCE_DIFF_PATIENT = "Patient information differs"
EVIDENCE_SAME_PATIENT = "Patient information is identical to prior claim"
EVIDENCE_DIFF_AMOUNT = "Invoice amount differs"
EVIDENCE_SAME_AMOUNT = "Invoice amount is identical to prior claim"

# Reason Language Mappings
REASON_TEMPLATE_CLONE = "Potential Fraudulent Reuse (Template Cloning)"
REASON_DUPLICATE = "Requires Investigation (Potential Duplicate Submission)"
REASON_GENERIC = "Suspicious Similarity (Generic Template Usage)"
REASON_LEGITIMATE = "Legitimate Template Reuse"
