# MedExtract (V2)
A scalable, Docker-ready Document Intelligence and Fraud Detection pipeline built to solve the IEEE problem statement: "Similar Document Template Matching Algorithm".

## Overview
This system identifies artificially tampered medical documents (invoices, lab reports, prescriptions) by generating a structural fingerprint of the underlying template, indexing it using FAISS, and detecting anomalies where identical templates are used across ostensibly different healthcare providers.

## Problem Statement
Medical invoices, prescriptions, and laboratory reports are frequently fraudulently reproduced using the same underlying digital or printed template. Bad actors simply change the provider name, logo, patient information, and amounts to fabricate claims. The system must detect similarity in the **UNDERLYING DOCUMENT TEMPLATE**, bypassing easily modified textual content.

## Proposed Methodology & Algorithm
Our algorithm relies on **Structural Fingerprinting**. 
1. Documents are deskewed and normalized. 
2. OpenCV morphology operations detect the underlying "skeleton" of the page (horizontal lines, vertical borders, table grids) while aggressively filtering out text.
3. This skeleton is embedded into a high-dimensional vector space alongside a visual layout embedding (MobileNetV3).
4. The system calculates L2 Euclidean Distance via Facebook AI Similarity Search (FAISS). 
5. The resulting **Risk Score** compares the structural match to the declared provider.

## Technology Justification
- **Frontend**: React + Vite + TailwindCSS ensures a lightning-fast, modern, investigative interface.
- **Backend**: FastAPI ensures high throughput and async capabilities, while Celery manages long-running computer vision tasks in the background.
- **AI Stack**: OpenCV (for raw layout extraction) and FAISS (for sub-millisecond vector similarity). Large Language Models are intentionally avoided to ensure strict deterministic CPU-friendly execution as per project constraints.
- **Deployment**: Full Docker Compose integration ensures the system is instantly demonstrable on any evaluator's machine without environment nightmares.

## Dataset & Evaluation
The system was evaluated against a synthetic dataset of medical invoices containing:
- Golden templates.
- Forged templates (structurally identical, completely different OCR text).
- Distinct templates.
The system consistently achieves extremely low FAISS L2 distances (<0.1) for forgeries, accurately isolating them from disparate templates.

## Limitations & Future Scope
- **Limitations**: Scans with heavy perspective distortion (taken at sharp angles with a mobile phone) can alter structural boxes.
- **Future Scope**: Implementing deep learning perspective-correction models and extending the fingerprinting to include font-style detection.

## Quickstart (Docker Compose)
The easiest way to run the entire stack (Frontend + Backend + DB + Redis + Workers) is via Docker.

```bash
# 1. Clone the repository
git clone https://github.com/your-org/medextract.git
cd medextract

# 2. Copy the example environment variables
cp .env.example .env

# 3. Start the cluster
docker-compose up -d --build
```

The system will now be available at:
- **Frontend UI**: `http://localhost`
- **Backend API Docs**: `http://localhost:8000/docs`

## Local Development (Without Docker)

### Backend
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Security & Production Readiness
This project has been hardened for production environments:
- File size and type validations prevent malicious uploads.
- `werkzeug.utils.secure_filename` prevents path traversal attacks.
- Temporary OCR files are strictly managed and deleted.
- Global 500 exception handlers prevent internal stack trace leakage.
- Strict CORS origins limit frontend access.
