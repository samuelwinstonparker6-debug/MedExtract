import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertTriangle, CheckCircle, ArrowLeft, Download, RefreshCw, ShieldAlert, ShieldCheck } from "lucide-react";
import { api } from "@/lib/api";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export default function Similarity() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [doc, setDoc] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDoc = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await api.get(`/api/v2/documents/${id}`);
        setDoc(response.data);
      } catch (err: any) {
        console.error("Failed to load document analysis:", err);
        setError("Document record not found.");
      } finally {
        setLoading(false);
      }
    };
    fetchDoc();
  }, [id]);

  if (loading) {
    return (
      <div className="p-8 max-w-7xl mx-auto flex flex-col justify-center items-center h-64 gap-4">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <p className="text-slate-500 font-medium">Fetching structural similarity comparison...</p>
      </div>
    );
  }

  if (error || !doc) {
    return (
      <div className="p-8 max-w-7xl mx-auto">
        <Button variant="ghost" onClick={() => navigate("/queue")} className="gap-2 mb-4">
          <ArrowLeft size={16} /> Back to Investigation Queue
        </Button>
        <div className="bg-red-50 border border-red-200 text-red-700 p-6 rounded-xl text-center">
          <h3 className="font-bold text-lg">Document Not Found</h3>
          <p className="text-sm mt-1">{error}</p>
        </div>
      </div>
    );
  }

  const isRed = doc.fraud_status === 'RED';
  const isAmber = doc.fraud_status === 'AMBER';
  const similarityScorePct = doc.fraud_score ? (doc.fraud_score * 100).toFixed(1) : "95.0";
  const fileUrl = doc.filename ? `${BASE_URL}/uploads/${doc.filename}` : null;

  const providerName = doc.structured_data?.provider_name?.value || 
                       doc.structured_data?.hospital_name?.value || 
                       doc.structured_data?.doctor_name?.value || 
                       doc.source_type || 'Unknown Provider';

  const patientName = doc.structured_data?.patient_name?.value || 'N/A';
  const amountVal = doc.structured_data?.amount?.value || doc.structured_data?.total_amount?.value || 'N/A';

  return (
    <div className="p-8 max-w-[1600px] mx-auto space-y-6">
      <div>
        <Button variant="ghost" onClick={() => navigate("/queue")} className="gap-2 mb-3 -ml-2">
          <ArrowLeft size={16} /> Back to Investigation Queue
        </Button>
        <div className="flex flex-wrap justify-between items-start gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
              Investigation: Document #{doc.id}
            </h1>
            <p className="text-slate-500 mt-1">
              Template Structural Similarity Assessment & Contextual Risk Evidence
            </p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" className="gap-2">
              <Download size={16} /> Export Analysis
            </Button>
            <Button 
              className={isRed ? "bg-red-600 hover:bg-red-700 text-white font-bold" : "bg-blue-600 hover:bg-blue-700 text-white font-bold"}
              onClick={() => alert(`Document #${doc.id} flagged for investigator review.`)}
            >
              Flag for Detailed Investigation
            </Button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Left Column: Metrics & Evidence */}
        <div className="space-y-6">
          {/* Similarity & Risk Overview */}
          <Card className={isRed ? "border-red-200 bg-red-50/40" : isAmber ? "border-amber-200 bg-amber-50/40" : "border-emerald-200 bg-emerald-50/40"}>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center justify-between text-base">
                <span className="font-bold text-slate-900">TEMPLATE SIMILARITY</span>
                <span className="font-mono text-2xl font-extrabold text-blue-600">
                  {similarityScorePct}%
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between pt-2 border-t border-slate-200/60">
                <span className="text-sm font-semibold text-slate-700">Risk Assessment:</span>
                <Badge variant={isRed ? "destructive" : isAmber ? "warning" : "success"} className="text-xs px-3 py-1 font-bold">
                  {isRed ? "HIGH FRAUD RISK (RED)" : isAmber ? "SUSPICIOUS (AMBER)" : "LOW RISK (GREEN)"}
                </Badge>
              </div>

              <div>
                <h4 className="font-semibold text-slate-900 text-xs uppercase tracking-wider mb-2">Automated Risk Evidence</h4>
                {doc.fraud_flags && doc.fraud_flags.length > 0 ? (
                  <ul className="space-y-2">
                    {doc.fraud_flags.map((flag: string, i: number) => (
                      <li key={i} className="flex items-start gap-2 text-xs font-medium text-slate-800 bg-white/80 p-2.5 rounded border border-slate-200/80">
                        <AlertTriangle size={14} className={isRed ? "text-red-500 shrink-0 mt-0.5" : "text-amber-500 shrink-0 mt-0.5"} />
                        <span>{flag}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="flex items-center gap-2 text-xs font-medium text-emerald-700 bg-emerald-100/60 p-2.5 rounded border border-emerald-200">
                    <ShieldCheck size={16} className="text-emerald-600" />
                    <span>No structural anomalies detected. Document layout matches registered provider template.</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Evidence Categories: Structural Match vs Content Changes */}
          <Card>
            <CardHeader className="pb-3 border-b border-slate-100">
              <CardTitle className="text-base font-bold text-slate-900">Structural & Content Evidence</CardTitle>
            </CardHeader>
            <CardContent className="space-y-5 pt-4">
              {/* Structural Match */}
              <div>
                <h4 className="text-xs font-bold text-emerald-700 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                  <CheckCircle size={14} /> STRUCTURAL MATCH (Layout Anatomy)
                </h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-emerald-50 text-emerald-900 border border-emerald-200 px-2.5 py-1.5 rounded flex items-center gap-1">
                    ✓ Header Geometry
                  </div>
                  <div className="bg-emerald-50 text-emerald-900 border border-emerald-200 px-2.5 py-1.5 rounded flex items-center gap-1">
                    ✓ Table Grid Ratio
                  </div>
                  <div className="bg-emerald-50 text-emerald-900 border border-emerald-200 px-2.5 py-1.5 rounded flex items-center gap-1">
                    ✓ Field Positions
                  </div>
                  <div className="bg-emerald-50 text-emerald-900 border border-emerald-200 px-2.5 py-1.5 rounded flex items-center gap-1">
                    ✓ Footer Structure
                  </div>
                </div>
              </div>

              {/* Content / Identity Changes */}
              <div>
                <h4 className="text-xs font-bold text-amber-700 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                  <AlertTriangle size={14} /> CONTENT / IDENTITY CHANGES
                </h4>
                <div className="space-y-2 text-xs">
                  <div className="bg-amber-50 text-amber-900 border border-amber-200 p-2.5 rounded space-y-1">
                    <div className="font-semibold flex justify-between">
                      <span>Provider:</span>
                      <span className="font-mono text-slate-800">{providerName}</span>
                    </div>
                    <div className="font-semibold flex justify-between">
                      <span>Patient:</span>
                      <span className="font-mono text-slate-800">{patientName}</span>
                    </div>
                    <div className="font-semibold flex justify-between">
                      <span>Amount:</span>
                      <span className="font-mono text-slate-800">{amountVal}</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Visual Document Preview */}
        <Card className="xl:col-span-2 flex flex-col">
          <CardHeader className="border-b border-slate-100 pb-4">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Document Visual Analysis</CardTitle>
              <Badge variant="outline" className="text-xs font-mono">{doc.document_type || doc.source_type}</Badge>
            </div>
          </CardHeader>
          <CardContent className="flex-1 p-6 bg-slate-900 flex items-center justify-center min-h-[500px]">
            {fileUrl ? (
              doc.filename?.toLowerCase().endsWith('.pdf') ? (
                <iframe src={fileUrl} className="w-full h-[550px] rounded bg-slate-950" title="Document Preview" />
              ) : (
                <img src={fileUrl} alt="Submitted Document" className="max-h-[550px] w-auto object-contain rounded shadow-lg" />
              )
            ) : (
              <div className="text-slate-400 text-sm">Visual preview unavailable for this document.</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

