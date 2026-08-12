import { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { Save, AlertCircle, RefreshCw, ShieldAlert, CheckCircle, Shield } from 'lucide-react';
import { api } from '@/lib/api';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

/**
 * Derive the public URL for a document image/PDF from its filename only.
 */
function getDocumentUrl(filename: string) {
  if (!filename) return null;
  return `${BASE_URL}/uploads/${filename}`;
}

export default function Analysis() {
  const { id } = useParams();
  const [document, setDocument] = useState<any>(null);
  const [formData, setFormData] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const pollingRef = useRef<any>(null);

  const fetchDocument = async () => {
    try {
      const response = await api.get(`/api/v2/documents/${id}`);
      const data = response.data;
      setDocument(data);
      if (data.structured_data) {
        setFormData(data.structured_data);
      }
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
    pollingRef.current = setInterval(fetchDocument, 3000);
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    };
  }, [id]);

  const handleInputChange = (key: string, val: string) => {
    setFormData((prev: any) => ({
      ...prev,
      [key]: { ...prev[key], value: val },
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage({ type: '', text: '' });
    try {
      await api.put(`/api/v2/documents/${id}/extracted`, formData);
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
      const response = await api.post(`/api/v2/documents/${id}/reprocess`);
      setFormData(response.data.structured_data || {});
      setDocument((prev: any) => ({ ...prev, ...response.data }));
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

  const isPending = document.status === 'pending' || document.status === 'extracted';
  const isFailed = document.status === 'failed';
  const fileUrl = getDocumentUrl(document.filename);

  const fraudColor = {
    RED: 'border-red-500/50 bg-red-900/20',
    AMBER: 'border-amber-500/50 bg-amber-900/20',
    NONE: 'border-emerald-500/30 bg-emerald-900/10',
  }[document.fraud_status as string] || 'border-gray-700 bg-gray-900/20';

  const fraudTextColor = {
    RED: 'text-red-400',
    AMBER: 'text-amber-400',
    NONE: 'text-emerald-400',
  }[document.fraud_status as string] || 'text-gray-400';

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6 text-slate-900">Document Analysis</h1>
      <div
        className={`grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-12rem)] rounded-xl transition-all duration-500 ${
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
            <div className="absolute top-4 left-4 z-20 bg-red-600 text-white font-bold px-6 py-3 rounded-lg shadow-2xl flex items-center gap-3 border-2 border-red-400 animate-pulse backdrop-blur-md text-lg uppercase">
              <ShieldAlert className="w-6 h-6" />
              <span className="tracking-[0.2em]">High Fraud Risk</span>
            </div>
          )}

          <div className="bg-surface/80 p-4 border-b border-slate-700 flex justify-between items-center bg-slate-800 text-white">
            <h2 className="font-bold text-lg">Document Preview</h2>
            <span className="text-sm text-slate-300 capitalize">{document.source_type}</span>
          </div>

          <div
            className={`flex-1 bg-slate-900 overflow-auto p-4 flex justify-center relative ${
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
              <div className="text-slate-500 text-sm flex items-center">Preview unavailable</div>
            )}
          </div>
        </div>

        {/* ── Right Pane: Extracted Data ── */}
        <div
          className={`glass-panel rounded-xl flex flex-col overflow-hidden bg-white shadow-xl ${
            document.fraud_status === 'RED' ? 'border-red-500/30' : ''
          }`}
        >
          <div className="bg-slate-800 text-white p-4 border-b border-slate-700 flex justify-between items-center">
            <h2 className="font-bold text-lg flex items-center gap-2">
              Extracted Data & Template Check
              {isPending && <RefreshCw className="w-4 h-4 animate-spin text-yellow-400" />}
            </h2>
            <span className="text-sm bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full uppercase tracking-wider font-semibold">
              {document.document_type || (document.status === 'completed' ? 'Completed' : document.status === 'failed' ? 'Failed' : 'Processing...')}
            </span>
          </div>

          <div className="flex-1 overflow-auto p-6 text-slate-800">
            {isPending ? (
              <div className="text-center text-slate-400 mt-12 flex flex-col items-center gap-4">
                <RefreshCw className="w-8 h-8 animate-spin text-primary" />
                <p>Pipeline is currently extracting document layout. Please wait…</p>
                <button onClick={fetchDocument} className="text-primary hover:underline mt-2">
                  Refresh Status
                </button>
              </div>
            ) : isFailed ? (
              <div className="text-center text-red-500 mt-12 flex flex-col items-center gap-2">
                <AlertCircle className="w-8 h-8 mb-2" />
                <p>Processing failed. Please try uploading again.</p>
              </div>
            ) : (
              <div className="space-y-6">
                {message.text && (
                  <div
                    className={`p-4 rounded-lg ${
                      message.type === 'success'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {message.text}
                  </div>
                )}

                {/* ── Fraud Risk Assessment Panel ── */}
                {document.fraud_status !== undefined && (
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
                            ? 'bg-red-900/40 text-red-400 border-red-500/50'
                            : document.fraud_status === 'AMBER'
                            ? 'bg-amber-900/40 text-amber-500 border-amber-500/50'
                            : 'bg-emerald-900/40 text-emerald-500 border-emerald-500/50'
                        }`}
                      >
                        Risk Score: {document.fraud_score != null ? `${(document.fraud_score * 100).toFixed(1)}%` : 'N/A'}
                      </span>
                    </div>

                    <div className="relative z-10">
                      {document.fraud_flags && document.fraud_flags.length > 0 ? (
                        <ul
                          className={`list-disc pl-5 space-y-2 text-sm mt-3 pt-3 border-t ${
                            document.fraud_status === 'RED'
                              ? 'border-red-500/30 text-red-700'
                              : 'border-amber-500/30 text-amber-700'
                          }`}
                        >
                          {document.fraud_flags.map((flag: string, i: number) => (
                            <li key={i} className="font-medium leading-relaxed">
                              {flag}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-sm text-emerald-700 mt-2 font-medium">
                          No suspicious structural patterns detected. Template matches expected provider structure.
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
                        ? 'bg-blue-50 border-blue-200'
                        : 'bg-orange-50 border-orange-200'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <Shield
                        className={`w-5 h-5 ${
                          document.reference_verification_result.startsWith('Verified')
                            ? 'text-blue-500'
                            : 'text-orange-500'
                        }`}
                      />
                      <h3
                        className={`font-bold text-lg ${
                          document.reference_verification_result.startsWith('Verified')
                            ? 'text-blue-700'
                            : 'text-orange-700'
                        }`}
                      >
                        Provider Template Verification
                      </h3>
                    </div>
                    <p
                      className={`text-sm font-medium ${
                        document.reference_verification_result.startsWith('Verified')
                          ? 'text-blue-600'
                          : 'text-orange-600'
                      }`}
                    >
                      {document.reference_verification_result}
                    </p>
                  </div>
                )}

                {/* ── Algorithm Version Badge ── */}
                {document.fingerprint_version && (
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-slate-100" />
                    <span className="text-xs text-slate-100">
                      Fingerprint Algorithm v{document.fingerprint_version} — Content-Invariant Structural Analysis
                    </span>
                  </div>
                )}

                {/* ── Extracted Fields ── */}
                <div className="space-y-4">
                  {Object.entries(formData).map(([key, data]: [string, any]) => {
                    if (key === 'raw_entities') return null;
                    const confidence = data?.confidence ?? 0;
                    const confColor =
                      confidence > 0.8
                        ? 'text-green-600'
                        : confidence > 0.5
                        ? 'text-yellow-600'
                        : 'text-red-600';
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
                          className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary transition-all"
                        />
                      </div>
                    );
                  })}
                </div>

                {/* ── Action Buttons ── */}
                <div className="pt-6 border-t border-slate-200 flex gap-4">
                  <button
                    onClick={handleReprocess}
                    disabled={saving}
                    className="w-1/3 flex items-center justify-center gap-2 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold py-3 rounded-lg transition-colors border border-slate-300"
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
                <div className="mt-8 pt-6 border-t border-slate-200">
                  <h3 className="text-sm font-medium text-slate-500 mb-2">Raw OCR Text</h3>
                  <pre className="bg-slate-50 border border-slate-200 p-4 rounded-lg text-xs text-slate-600 whitespace-pre-wrap font-mono overflow-auto max-h-40">
                    {document.extracted_text || '(no text extracted)'}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
