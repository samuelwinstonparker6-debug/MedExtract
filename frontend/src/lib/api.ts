import axios from "axios";

// Connect to the FastAPI backend
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "", // Default to proxy
  headers: {
    "Content-Type": "application/json",
    "X-API-Key": "dev-insecure-key-change-in-production"
  },
});

export interface RiskAssessment {
  risk_score: number;
  risk_level: "GREEN" | "AMBER" | "RED";
  confidence: number;
  reasons: string[];
  evidence: string[];
  matched_documents: string[];
  matched_template_id: string;
}

export interface ExplanationResult {
  original_document_id: string;
  matched_template_id: string;
  risk_assessment: RiskAssessment;
  visual_comparison_image_url: string;
  stable_regions: any[];
  changed_regions: any[];
}
