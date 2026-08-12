# MedExtract V2 Architecture

## Overview
The V2 Architecture explicitly targets the problem of **Template Fingerprinting and Structural Similarity**, moving away from pure-text OCR comparison to layout-based structural comparison. 

## 1. Document Preprocessing (`app/engine/preprocessing.py`)
Incoming documents (PDFs or Images) pass through a rigorous normalisation pipeline:
- Rasterization to 300 DPI
- Normalised scaling to 2400px height.
- Deskewing (detects arbitrary rotation and corrects to 0 degrees).
- Contrast CLAHE and FastNlMeansDenoising.

## 2. Layout Understanding (`app/engine/layout.py`)
Instead of just reading text, OpenCV and contours are used to identify:
- Horizontal/Vertical lines
- Table grids
- Image/Logo placeholders
- The relative coordinate locations of these items are normalised (0.0 to 1.0).

## 3. Structural Fingerprinting (`app/engine/fingerprint.py`)
A deterministic dictionary mapping out the skeleton of the document (margins, table rows, signature boxes). Any dynamic text (patient name, date, invoice amount) is intentionally ignored.

## 4. FAISS Similarity Engine (`app/engine/similarity.py`)
To prevent O(N^2) brute force comparisons, fingerprints are embedded into a 140-dimensional fixed vector space representing layout geometries, concatenated with a 1000-dimensional visual feature space via MobileNetV3. 
- Fast Euclidean distance (L2) search is performed using Facebook AI Similarity Search (FAISS).

## 5. Risk Engine (`app/engine/risk_engine.py`)
Similarity != Fraud. 
The Risk Engine applies business logic to structural matches. 
- **Green**: Known template, matches known provider.
- **Amber**: Unknown template, minor discrepancies.
- **Red**: Highly structurally similar, but the claimed Provider is different (Template Cloning).

## 6. Worker Service (`app/services/worker_service.py`)
All heavy AI operations are pushed to a background thread to allow the FastAPI layer to instantly return a `202 Accepted` to the client.
