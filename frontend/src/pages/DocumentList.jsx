import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '@/lib/api';
import { FileText, Clock, CheckCircle, AlertCircle, Trash2 } from 'lucide-react';

export default function DocumentList() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await api.get('/api/v2/documents');
      setDocuments(response.data);
    } catch (error) {
      console.error("Error fetching documents:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm(`Are you sure you want to delete document #${id}?`)) return;
    try {
      await api.delete(`/api/v2/documents/${id}`);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch (error) {
      console.error("Error deleting document:", error);
      alert("Failed to delete document.");
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm("Are you sure you want to delete ALL documents? This cannot be undone.")) return;
    try {
      await api.delete('/api/v2/documents');
      setDocuments([]);
    } catch (error) {
      console.error("Error clearing documents:", error);
      alert("Failed to clear documents.");
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'pending':
        return <span className="flex items-center gap-1 bg-yellow-500/20 text-yellow-400 px-3 py-1 rounded-full text-sm font-medium"><Clock className="w-4 h-4" /> Processing</span>;
      case 'text_extracted':
        return <span className="flex items-center gap-1 bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full text-sm font-medium"><FileText className="w-4 h-4" /> Text Extracted</span>;
      case 'extracted':
        return <span className="flex items-center gap-1 bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-sm font-medium"><CheckCircle className="w-4 h-4" /> Extracted</span>;
      default:
        return <span className="flex items-center gap-1 bg-red-500/20 text-red-400 px-3 py-1 rounded-full text-sm font-medium"><AlertCircle className="w-4 h-4" /> Failed</span>;
    }
  };

  const getFraudBadge = (status) => {
    switch (status) {
      case 'RED':
        return <span className="flex items-center gap-1 bg-[var(--color-fraud-red-bg)] text-[var(--color-fraud-red)] px-3 py-1 rounded-full text-sm font-bold border border-red-500/30 glow-red animate-pulse-subtle"><AlertCircle className="w-4 h-4" /> High Risk</span>;
      case 'AMBER':
        return <span className="flex items-center gap-1 bg-[var(--color-fraud-amber-bg)] text-[var(--color-fraud-amber)] px-3 py-1 rounded-full text-sm font-semibold border border-amber-500/30"><AlertCircle className="w-4 h-4" /> Suspicious</span>;
      case 'NONE':
      default:
        return <span className="flex items-center gap-1 bg-[var(--color-fraud-safe-bg)] text-[var(--color-fraud-safe)] px-3 py-1 rounded-full text-sm font-medium border border-emerald-500/20"><CheckCircle className="w-4 h-4" /> Safe</span>;
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div></div>;
  }

  return (
    <div className="glass-panel rounded-xl p-8 transition-all">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-primary">Document Dashboard</h1>
        <div className="flex gap-3">
          {documents.length > 0 && (
            <button 
              onClick={handleClearAll} 
              className="flex items-center gap-1.5 px-4 py-2 bg-red-600/20 hover:bg-red-600/40 text-red-400 rounded-lg border border-red-500/30 text-sm font-medium transition-colors"
            >
              <Trash2 className="w-4 h-4" /> Clear All Documents
            </button>
          )}
          <button onClick={fetchDocuments} className="px-4 py-2 bg-surface hover:bg-surface-hover rounded-lg border border-gray-700 text-sm font-medium transition-colors">Refresh</button>
        </div>
      </div>
      
      <div className="overflow-x-auto rounded-lg border border-gray-800 bg-surface/50">
        <table className="w-full text-left border-collapse">
          <thead className="bg-gray-800/80">
            <tr>
              <th className="py-4 px-4 font-semibold text-gray-400">ID</th>
              <th className="py-4 px-4 font-semibold text-gray-400">Source Type</th>
              <th className="py-4 px-4 font-semibold text-gray-400">Document Type</th>
              <th className="py-4 px-4 font-semibold text-gray-400">Fraud Status</th>
              <th className="py-4 px-4 font-semibold text-gray-400">Status</th>
              <th className="py-4 px-4 font-semibold text-gray-400 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.id} className="border-b border-gray-800/50 hover:bg-gray-800/80 transition-colors">
                <td className="py-4 px-4 font-medium">#{doc.id}</td>
                <td className="py-4 px-4 capitalize">{doc.source_type}</td>
                <td className="py-4 px-4 capitalize font-medium">{doc.document_type || '-'}</td>
                <td className="py-4 px-4">{getFraudBadge(doc.fraud_status || 'NONE')}</td>
                <td className="py-4 px-4">{getStatusBadge(doc.status)}</td>
                <td className="py-4 px-4 text-right flex items-center justify-end gap-3">
                  <Link to={`/documents/${doc.id}`} className="text-primary hover:text-blue-400 font-semibold transition-colors flex items-center gap-1">
                    View Details
                  </Link>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    title="Delete Document"
                    className="text-red-400 hover:text-red-300 transition-colors p-1 hover:bg-red-500/10 rounded"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
            {documents.length === 0 && (
              <tr>
                <td colSpan="6" className="py-12 text-center text-gray-500">
                  <FileText className="w-12 h-12 mx-auto mb-3 opacity-20" />
                  No documents found. Upload one to get started.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

