# Template Fingerprinting Methodology

The MedExtract Template Fingerprinting Engine addresses the core challenge of medical document fraud: proving that a document's layout structurally matches a stolen template, even if the textual content (patient names, dates, amounts) has been completely altered.

To achieve this, MedExtract completely ignores the textual content of OCR and instead analyzes the geometric and spatial structure of the document.

## 1. Spatial Density Grid (50% Weight)
We divide the document into a normalized `10x10` grid. For every bounding box detected by the OCR engine, we calculate its area contribution to the underlying grid cells. This creates a density map of ink across the page.
- **Why?** It captures the macro-layout of paragraphs, headers, and tables. Since it relies on bounding box area rather than string length, dynamic text changes (e.g., "John Doe" vs "Christopher Columbus") result in minimal density variance.

## 2. Alignment Histograms (40% Weight)
We capture the underlying margins and row structures by creating histograms (20 bins) of the X and Y coordinates of every bounding box.
- **X-Alignment (20%)**: Captures left-margins, column starts, and indentation rules.
- **Y-Alignment (20%)**: Captures line spacing, row heights, and section breaks.

## 3. Structural Region Anchors (10% Weight)
The pipeline leverages heuristic OpenCV rules to identify distinct visual anchors, extracting their $(X, Y)$ centroids.
- Headers
- Footers
- Tables (via grid line intersection)
- Logos/Images (via contour analysis)
- Barcodes (via pyzbar)

## Normalization and Determinism
Every coordinate is normalized against the total width and height of the image to scale between `[0, 1]`. This ensures that a heavily compressed JPEG and a high-resolution PDF scan of the same template produce mathematically identical structural fingerprints.

## Similarity Calculation
When comparing a submitted claim against a database of known provider templates, MedExtract calculates the structural distance:
1. **Cosine Similarity** is applied to the Spatial Density Grids and Alignment Histograms.
2. **Euclidean Distance** measures the drift of Structural Region Anchors. Missing anchors apply a standardized penalty.
3. The final weighted sum generates a score `[0.0, 1.0]`.

Documents scoring $>0.98$ to a known template, while claiming to be from a different provider, are instantly flagged as **RED** (Template Reuse/Cloning).
