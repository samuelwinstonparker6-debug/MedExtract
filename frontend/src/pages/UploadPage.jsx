import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '@/lib/api';
import { Upload, FileUp, CheckCircle, AlertCircle } from 'lucide-react';

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [sourceType, setSourceType] = useState('doctor');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('source_type', sourceType);

    try {
      const response = await api.post(`/api/v2/documents/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      navigate(`/documents/${response.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "An error occurred during upload.");
      setUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="glass-panel rounded-xl p-8">
        <h1 className="text-2xl font-bold mb-2">Upload Document</h1>
        <p className="text-gray-400 mb-8">Upload a medical invoice, prescription, or lab report to extract data.</p>
        
        {error && (
          <div className="mb-6 bg-red-500/20 text-red-400 p-4 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5" />
            {error}
          </div>
        )}

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">Source Type</label>
          <select 
            value={sourceType} 
            onChange={(e) => setSourceType(e.target.value)}
            className="w-full bg-surface border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-primary transition-all"
          >
            <option value="doctor">Doctor</option>
            <option value="hospital">Hospital</option>
            <option value="lab">Lab</option>
            <option value="customer">Customer</option>
          </select>
        </div>

        <div 
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          className="border-2 border-dashed border-gray-600 rounded-xl p-12 text-center hover:border-primary transition-colors cursor-pointer mb-8"
          onClick={() => document.getElementById('file-upload').click()}
        >
          <input 
            type="file" 
            id="file-upload" 
            className="hidden" 
            onChange={(e) => setFile(e.target.files[0])}
            accept=".pdf,.jpg,.jpeg,.png"
          />
          {file ? (
            <div className="flex flex-col items-center">
              <CheckCircle className="w-12 h-12 text-green-500 mb-4" />
              <p className="text-lg font-medium text-white">{file.name}</p>
              <p className="text-sm text-gray-400 mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <Upload className="w-12 h-12 text-gray-400 mb-4" />
              <p className="text-lg font-medium text-white">Drag & drop your file here</p>
              <p className="text-sm text-gray-400 mt-1">Supports PDF, JPG, PNG</p>
            </div>
          )}
        </div>

        <button 
          onClick={handleUpload}
          disabled={!file || uploading}
          className={`w-full flex items-center justify-center gap-2 py-4 rounded-lg font-bold text-lg transition-all ${!file || uploading ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-primary hover:bg-blue-600 text-white shadow-lg shadow-blue-500/30'}`}
        >
          {uploading ? (
            <><div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div> Uploading...</>
          ) : (
            <><FileUp className="w-5 h-5" /> Process Document</>
          )}
        </button>
      </div>
    </div>
  );
}
