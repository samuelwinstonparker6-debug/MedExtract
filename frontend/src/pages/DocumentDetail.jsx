import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { Save, AlertCircle, RefreshCw, ShieldAlert, CheckCircle, Shield } from 'lucide-react';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
const API_KEY = import.meta.env.VITE_API_KEY || '';

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { 'X-API-Key': API_KEY },
});

/**
 * Derive the public URL for a document image/PDF from its filename only.
 * Never uses file_path (a server-side absolute path).
 */
function getDocumentUrl(filename) {
  if (!filename) return null;
  // filename is the UUID-based filename (e.g. "a3f2b1c4-....pdf")
  return `${BASE_URL}/uploads/${filename}`;
}

export default function DocumentDetail() {
  const { id } = useParams();
  const [document, setDocument] = useState(null);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Use a ref for the polling interval so it doesn't trigger re-renders
  const pollingRef = useRef(null);

  const fetchDocument = async () => {
    try {
      const response = await apiClient.get(`/api/v2/documents/${id}`);
      const data = response.data;
      setDocument(data);
      if (data.structured_data) {
        setFormData(data.structured_data);
      }
      // Stop polling once processing is done
      if (data.status === 'completed' || data.status === 'failed') {
        if (pollingRef.current) {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
      }
    } catch (error) {
      console.error('Error fetching document:', error);
      setMessage({ type: 'error', text: 'Failed to load document.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocument();
    // Start polling — will be stopped by fetchDocument when status is terminal
    pollingRef.current = setInterval(fetchDocument, 1000);
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]); // Only re-run if the document ID changes

  const handleInputChange = (key, val) => {
    setFormData(prev => ({
      ...prev,
      [key]: { ...prev[key], value: val },
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage({ type: '', text: '' });
    try {
      await apiClient.put(`/api/v2/documents/${id}/extracted`, formData);
      setMessage({ type: 'success', text: 'Corrections saved successfully!' });
    } catch {
      setMessage({ type: 'error', text: 'Failed to save corrections.' });
    } finally {
      setSaving(false);
    }
  };

  const handleReprocess = async () => {
    setSaving(true);
    setMessage({ type: '', text: '' });
    try {
      const response = await apiClient.post(`/api/v2/documents/${id}/reprocess`);
      setFormData(response.data.structured_data || {});
      setDocument(prev => ({ ...prev, ...response.data }));
      setMessage({ type: 'success', text: 'Document reprocessed successfully!' });
    } catch {
      setMessage({ type: 'error', text: 'Failed to reprocess document.' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  if (!document) {
    return (
      <div className="text-center text-red-400 p-8 glass-panel rounded-xl">
        Document not found
      </div>
    );
  }

  const isTerminal = document.status === 'completed' || document.status === 'failed';
  const showExtractedData = ['extracted', 'similarity_search', 'completed'].includes(document.status);
  const isFailed = document.status === 'failed';
  const isFailed = document.status === 'failed';
  const fileUrl = getDocumentUrl(document.filename);

  const fraudColor = {
    RED: 'border-red-500/50 bg-red-900/20',
    AMBER: 'border-amber-500/50 bg-amber-900/20',
    NONE: 'border-emerald-500/30 bg-emerald-900/10',
  }[document.fraud_status] || 'border-gray-700 bg-gray-900/20';

  const fraudTextColor = {
    RED: 'text-red-400',
    AMBER: 'text-amber-400',
    NONE: 'text-emerald-400',
  }[document.fraud_status] || 'text-gray-400';

  // Helper for progress tracker
  const getStepStatus = (stepName) => {
    const states = [
      'pending', 
      'preprocessing', 
      'ocr_processing', 
      'fingerprinting', 
      'extracted', 
      'similarity_search', 
      'completed'
    ];
    const currentIndex = states.indexOf(document.status);
    if (currentIndex === -1) return 'pending';

    switch(stepName) {
      case 'received':
        return 'completed';
      case 'ocr':
        return currentIndex >= states.indexOf('fingerprinting') ? 'completed' : (currentIndex >= states.indexOf('preprocessing') ? 'active' : 'pending');
      case 'template':
        return currentIndex >= states.indexOf('extracted') ? 'completed' : (currentIndex >= states.indexOf('fingerprinting') ? 'active' : 'pending');
      case 'similarity':
        return currentIndex >= states.indexOf('completed') ? 'completed' : (currentIndex >= states.indexOf('similarity_search') ? 'active' : 'pending');
      default:
        return 'pending';
    }
  };

  const renderStep = (label, status) => (
    <div className="flex items-center gap-3">
      {status === 'completed' ? (
        <CheckCircle className="w-5 h-5 text-green-500" />
      ) : status === 'active' ? (
        <RefreshCw className="w-5 h-5 animate-spin text-blue-400" />
      ) : (
        <div className="w-5 h-5 rounded-full border-2 border-gray-600" />
      )}
      <span className={status === 'completed' ? 'text-gray-300' : status === 'active' ? 'text-blue-300 font-bold' : 'text-gray-600'}>
        {label}
      </span>
    </div>
  );

  return (
    <div
      className={`grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-8rem)] rounded-xl transition-all duration-500 ${
        document.fraud_status === 'RED'
          ? 'ring-4 ring-red-500 bg-red-900/10 shadow-[0_0_80px_rgba(239,68,68,0.2)]'
          : ''
      }`}
    >
      {/* ── Left Pane: Document Preview ── */}
      <div
        className={`glass-panel rounded-xl flex flex-col overflow-hidden relative ${
          document.fraud_status === 'RED' ? 'border-red-500/30' : ''
        }`}
      >
        {document.fraud_status === 'RED' && (
          <div className="absolute top-4 left-4 z-20 bg-red-600 text-white font-bold px-6 py-3 rounded-lg shadow-2xl flex items-center gap-3 border-2 border-red-400 animate-pulse backdrop-blur-md text-xl uppercase">
            <ShieldAlert className="w-6 h-6" />
            <span className="tracking-[0.3em]">High Fraud Risk — Investigation Required</span>
          </div>
        )}

        <div className="bg-surface/80 p-4 border-b border-gray-700 flex justify-between items-center">
          <h2 className="font-bold text-lg">Document Preview</h2>
          <span className="text-sm text-gray-400 capitalize">{document.source_type}</span>
        </div>

        <div
          className={`flex-1 bg-gray-900 overflow-auto p-4 flex justify-center relative ${
            document.fraud_status === 'RED'
              ? 'after:content-[""] after:absolute after:inset-0 after:bg-red-500/10 after:pointer-events-none'
              : ''
          }`}
        >
          {fileUrl ? (
            document.filename?.toLowerCase().endsWith('.pdf') ? (
              <iframe src={fileUrl} className="w-full h-full rounded bg-slate-950 relative z-10" title="PDF Preview" />
            ) : (
              <img src={fileUrl} alt="Document" className="max-w-full h-auto object-contain rounded relative z-10" />
            )
          ) : (
            <div className="text-gray-500 text-sm flex items-center">Preview unavailable</div>
          )}
        </div>
      </div>

      {/* ── Right Pane: Extracted Data ── */}
      <div
        className={`glass-panel rounded-xl flex flex-col overflow-hidden ${
          document.fraud_status === 'RED' ? 'border-red-500/30' : ''
        }`}
      >
        <div className="bg-surface/80 p-4 border-b border-gray-700 flex justify-between items-center">
          <h2 className="font-bold text-lg flex items-center gap-2">
            Extracted Data
            {!isTerminal && <RefreshCw className="w-4 h-4 animate-spin text-yellow-400" />}
            {showExtractedData && !isTerminal && <span className="text-xs text-yellow-400 flex items-center gap-1"><RefreshCw className="w-3 h-3 animate-spin" /> Running Advanced Search...</span>}
          </h2>
          <span className="text-sm bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full uppercase tracking-wider font-semibold">
            {document.document_type || (document.status === 'completed' ? 'Completed' : document.status === 'failed' ? 'Failed' : 'Processing...')}
          </span>
        </div>

        <div className="flex-1 overflow-auto p-6">
          {!showExtractedData ? (
            <div className="text-center mt-8 flex flex-col items-center gap-6">
              <div className="bg-gray-900/50 p-6 rounded-xl border border-gray-700 w-full max-w-sm text-left flex flex-col gap-4">
                {renderStep('Document received', getStepStatus('received'))}
                {renderStep('OCR completed', getStepStatus('ocr'))}
                {renderStep('Template analysis completed', getStepStatus('template'))}
                {renderStep('Similarity analysis completed', getStepStatus('similarity'))}
              </div>
            </div>
          ) : isFailed ? (
            <div className="text-center text-red-400 mt-12 flex flex-col items-center gap-2">
              <AlertCircle className="w-8 h-8 mb-2" />
              <p>Processing failed. Please try uploading again.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {message.text && (
                <div
                  className={`p-4 rounded-lg ${
                    message.type === 'success'
                      ? 'bg-green-500/20 text-green-400'
                      : 'bg-red-500/20 text-red-400'
                  }`}
                >
                  {message.text}
                </div>
              )}

              {/* ── Fraud Analysis Panel ── */}
              {document.status === 'extracted' || document.status === 'similarity_search' ? (
                <div className="p-5 rounded-xl border border-gray-700 bg-gray-900/20 flex flex-col items-center justify-center py-8">
                   <RefreshCw className="w-8 h-8 animate-spin text-blue-400 mb-4" />
                   <p className="text-blue-300 font-medium">Running advanced structural similarity search...</p>
                   <p className="text-xs text-gray-500 mt-2">Checking template authenticity</p>
                </div>
              ) : document.fraud_status !== undefined && (
                <div className={`p-5 rounded-xl border relative overflow-hidden transition-all duration-300 ${fraudColor}`}>
                  <div className="flex justify-between items-center mb-3 relative z-10">
                    <h3 className={`font-bold flex items-center gap-2 text-lg ${fraudTextColor}`}>
                      <ShieldAlert
                        className={`w-6 h-6 ${document.fraud_status === 'RED' ? 'animate-pulse' : ''}`}
                      />
                      Template Risk Assessment:{' '}
                      {document.fraud_status === 'RED'
                        ? 'High Fraud Risk — Investigation Required'
                        : document.fraud_status === 'AMBER'
                        ? 'Suspicious Layout — Review Needed'
                        : 'Low Risk — Clear'}
                    </h3>
                    <span
                      className={`font-mono text-xs px-3 py-1 rounded border font-semibold ${
                        document.fraud_status === 'RED'
                          ? 'bg-red-900/40 text-red-300 border-red-500/50'
                          : document.fraud_status === 'AMBER'
                          ? 'bg-amber-900/40 text-amber-300 border-amber-500/50'
                          : 'bg-emerald-900/40 text-emerald-300 border-emerald-500/50'
                      }`}
                    >
                      Score: {document.fraud_score != null ? `${(document.fraud_score * 100).toFixed(1)}%` : 'N/A'}
                    </span>
                  </div>

                  <div className="relative z-10">
                    {document.fraud_flags && document.fraud_flags.length > 0 ? (
                      <ul
                        className={`list-disc pl-5 space-y-2 text-sm mt-3 pt-3 border-t ${
                          document.fraud_status === 'RED'
                            ? 'border-red-500/30 text-red-200'
                            : 'border-amber-500/30 text-amber-200'
                        }`}
                      >
                        {document.fraud_flags.map((flag, i) => (
                          <li key={i} className="font-medium leading-relaxed">
                            {flag}
                          </li>
                        ))}
                      </ul>
                    ) : (
                        <p className="text-sm text-emerald-200/80 mt-2 font-medium">
                        No suspicious structural patterns detected. Template appears low risk.
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* ── Reference Verification Panel ── */}
              {document.reference_verification_result && (
                <div
                  className={`p-5 rounded-xl border relative overflow-hidden transition-all duration-300 ${
                    document.reference_verification_result.startsWith('Verified')
                      ? 'bg-blue-900/20 border-blue-500/50'
                      : 'bg-orange-900/20 border-orange-500/50'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Shield
                      className={`w-5 h-5 ${
                        document.reference_verification_result.startsWith('Verified')
                          ? 'text-blue-400'
                          : 'text-orange-400'
                      }`}
                    />
                    <h3
                      className={`font-bold text-lg ${
                        document.reference_verification_result.startsWith('Verified')
                          ? 'text-blue-400'
                          : 'text-orange-400'
                      }`}
                    >
                      Provider Template Verification
                    </h3>
                  </div>
                  <p
                    className={`text-sm font-medium ${
                      document.reference_verification_result.startsWith('Verified')
                        ? 'text-blue-200'
                        : 'text-orange-200'
                    }`}
                  >
                    {document.reference_verification_result}
                  </p>
                </div>
              )}

              {/* ── Algorithm Version Badge ── */}
              {document.fingerprint_version && (
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-gray-500" />
                  <span className="text-xs text-gray-500">
                    Fingerprint Algorithm v{document.fingerprint_version} — Content-Invariant Structural Analysis
                  </span>
                </div>
              )}

              {/* ── Extracted Fields ── */}
              <div className="space-y-4">
                {Object.entries(formData).map(([key, data]) => {
                  if (key === 'raw_entities') return null;
                  const confidence = data?.confidence ?? 0;
                  const confColor =
                    confidence > 0.8
                      ? 'text-green-400'
                      : confidence > 0.5
                      ? 'text-yellow-400'
                      : 'text-red-400';
                  return (
                    <div key={key}>
                      <div className="flex justify-between items-end mb-1">
                        <label className="block text-sm font-medium text-slate-100 capitalize">
                          {key.replace(/_/g, ' ')}
                        </label>
                        <span className={`text-xs font-semibold ${confColor}`}>
                          {(confidence * 100).toFixed(0)}% Confidence
                        </span>
                      </div>
                      <input
                        type="text"
                        value={data?.value || ''}
                        onChange={e => handleInputChange(key, e.target.value)}
                        className="w-full bg-background border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-primary transition-all"
                      />
                    </div>
                  );
                })}
              </div>

              {/* ── Action Buttons ── */}
              <div className="pt-6 border-t border-gray-700 flex gap-4">
                <button
                  onClick={handleReprocess}
                  disabled={saving}
                  className="w-1/3 flex items-center justify-center gap-2 bg-surface hover:bg-gray-700 text-white font-bold py-3 rounded-lg transition-colors border border-gray-600"
                >
                  <RefreshCw className={`w-5 h-5 ${saving ? 'animate-spin' : ''}`} />
                  Reprocess
                </button>
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="w-2/3 flex items-center justify-center gap-2 bg-primary hover:bg-blue-600 text-white font-bold py-3 rounded-lg transition-colors shadow-lg shadow-blue-500/20"
                >
                  <Save className="w-5 h-5" />
                  Save Corrections
                </button>
              </div>

              {/* ── Raw OCR Text ── */}
              <div className="mt-8 pt-6 border-t border-gray-700">
                <h3 className="text-sm font-medium text-gray-400 mb-2">Raw OCR Text</h3>
                <pre className="bg-background p-4 rounded-lg text-xs text-gray-500 whitespace-pre-wrap font-mono overflow-auto max-h-40">
                  {document.extracted_text || '(no text extracted)'}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
