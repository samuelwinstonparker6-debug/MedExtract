import { useState, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { UploadCloud, File, CheckCircle, Loader2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api";

export default function Upload() {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleProcess = async () => {
    if (!file) return;
    setIsProcessing(true);
    
    const formData = new FormData();
    formData.append("file", file);
    formData.append("source_type", "doctor"); // Default for now
    
    try {
      const response = await api.post("/api/v2/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      // Document is processing in background, go to Queue
      navigate(`/analysis/${response.data.id}`);
    } catch (error) {
      console.error("Upload failed", error);
      alert("Failed to upload document");
      setIsProcessing(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Upload Documents</h1>
        <p className="text-slate-500 mt-1">Ingest invoices, prescriptions, and lab reports into the pipeline.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>File Ingestion</CardTitle>
        </CardHeader>
        <CardContent>
          <input 
            type="file" 
            ref={fileInputRef} 
            className="hidden" 
            onChange={handleFileChange} 
            accept=".pdf,.png,.jpg,.jpeg,.webp" 
          />
          {!file ? (
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
                isDragging ? "border-blue-500 bg-blue-50" : "border-slate-200 bg-slate-50 hover:bg-slate-100"
              }`}
            >
              <div className="flex justify-center mb-4">
                <div className="h-16 w-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center">
                  <UploadCloud size={32} />
                </div>
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-1">Drag and drop a document</h3>
              <p className="text-sm text-slate-500 mb-6">Supports PDF, PNG, JPG up to 10MB</p>
              <Button onClick={() => fileInputRef.current?.click()}>Browse Files</Button>
            </div>
          ) : (
            <div className="border rounded-xl p-6 bg-slate-50 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 bg-white border border-slate-200 text-slate-400 rounded-lg flex items-center justify-center">
                  <File size={24} />
                </div>
                <div>
                  <p className="font-semibold text-slate-900">{file.name}</p>
                  <p className="text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
              <div>
                {!isProcessing ? (
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={() => setFile(null)}>Cancel</Button>
                    <Button onClick={handleProcess}>Process Document</Button>
                  </div>
                ) : (
                  <Button disabled className="gap-2">
                    <Loader2 size={16} className="animate-spin" /> Analyzing Layout...
                  </Button>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
      
      <div className="mt-8">
        <h3 className="text-lg font-semibold mb-4">Processing Pipeline</h3>
        <div className="space-y-3">
          <div className="flex items-center gap-3 text-slate-400">
            <CheckCircle size={20} className={isProcessing ? "text-emerald-500" : ""} />
            <span className={isProcessing ? "text-slate-900 font-medium" : ""}>1. Optical Character Recognition (OCR)</span>
          </div>
          <div className="flex items-center gap-3 text-slate-400">
            <CheckCircle size={20} />
            <span>2. Layout Geometry Extraction</span>
          </div>
          <div className="flex items-center gap-3 text-slate-400">
            <CheckCircle size={20} />
            <span>3. FAISS Structural Similarity Search</span>
          </div>
          <div className="flex items-center gap-3 text-slate-400">
            <CheckCircle size={20} />
            <span>4. Contextual Risk Scoring</span>
          </div>
        </div>
      </div>
    </div>
  );
}
