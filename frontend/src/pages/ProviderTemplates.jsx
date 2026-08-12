import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { UploadCloud, CheckCircle, FileText, Plus } from 'lucide-react';

export default function ProviderTemplates() {
  const [templates, setTemplates] = useState({ hospital: [], doctor: [], lab: [] });
  const [activeTab, setActiveTab] = useState('hospital');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [file, setFile] = useState(null);
  const [label, setLabel] = useState('');
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  const fetchTemplates = async () => {
    try {
      const response = await api.get('/api/v2/provider-templates');
      setTemplates(response.data);
    } catch (error) {
      console.error("Failed to fetch templates:", error);
    }
  };

  useEffect(() => {
    fetchTemplates();
  }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || !label) {
      setMessage('Please select a file and enter a label.');
      return;
    }

    setUploading(true);
    setMessage('');
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', activeTab);
    formData.append('label', label);

    try {
      await api.post('/api/v2/provider-templates/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setMessage('Template registered successfully!');
      setFile(null);
      setLabel('');
      fetchTemplates();
      setTimeout(() => setIsModalOpen(false), 1500);
    } catch (error) {
      console.error("Upload error:", error);
      setMessage('Failed to register template.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="flex justify-between items-center bg-surface p-6 rounded-xl border border-gray-700">
        <div>
          <h1 className="text-3xl font-bold mb-2">Provider Templates</h1>
          <p className="text-gray-400">Register genuine templates for automatic structural verification.</p>
        </div>
        <button
          onClick={() => { setIsModalOpen(true); setMessage(''); }}
          className="flex items-center gap-2 bg-primary hover:bg-blue-600 px-6 py-3 rounded-xl font-bold shadow-lg shadow-blue-500/20 transition-all"
        >
          <Plus className="w-5 h-5" />
          Add Reference
        </button>
      </div>

      <div className="flex gap-4 border-b border-gray-700 pb-2">
        {['hospital', 'doctor', 'lab'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-6 py-2 rounded-lg font-bold capitalize transition-colors ${
              activeTab === tab ? 'bg-primary text-white shadow-md' : 'text-gray-400 hover:bg-gray-800'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates[activeTab]?.length === 0 ? (
          <div className="col-span-full text-center py-12 text-gray-500 glass-panel rounded-xl">
            <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No registered templates for this category yet.</p>
          </div>
        ) : (
          templates[activeTab]?.map((ref) => (
            <div key={ref.id} className="glass-panel p-6 rounded-xl border border-gray-700 flex flex-col items-center text-center hover:border-primary transition-colors group">
              <CheckCircle className="w-10 h-10 text-emerald-400 mb-4 group-hover:scale-110 transition-transform" />
              <h3 className="font-bold text-lg mb-2">{ref.label}</h3>
              <p className="text-sm text-gray-400 font-mono">ID: {ref.id}</p>
              <p className="text-xs text-gray-500 mt-2">Registered: {new Date(ref.date_registered).toLocaleDateString()}</p>
            </div>
          ))
        )}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-surface border border-gray-700 p-8 rounded-2xl max-w-md w-full shadow-2xl">
            <h2 className="text-2xl font-bold mb-4 capitalize">Add {activeTab} Template</h2>
            
            {message && (
              <div className={`p-4 mb-4 rounded-lg font-medium text-center ${message.includes('success') ? 'bg-emerald-900/30 text-emerald-400 border border-emerald-500/30' : 'bg-red-900/30 text-red-400 border border-red-500/30'}`}>
                {message}
              </div>
            )}

            <form onSubmit={handleUpload} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Template Label</label>
                <input
                  type="text"
                  value={label}
                  onChange={(e) => setLabel(e.target.value)}
                  placeholder="e.g. Sunrise Health Medical Center - Invoice"
                  className="w-full bg-background border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Reference Image</label>
                <div className="border-2 border-dashed border-gray-600 rounded-xl p-8 text-center hover:border-primary transition-colors cursor-pointer bg-background relative">
                  <input
                    type="file"
                    onChange={(e) => setFile(e.target.files[0])}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    accept="image/*,application/pdf"
                    required
                  />
                  <UploadCloud className="w-10 h-10 mx-auto text-gray-400 mb-2" />
                  <p className="text-sm font-medium text-gray-300">
                    {file ? file.name : "Drag & drop or click to upload"}
                  </p>
                </div>
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="flex-1 bg-gray-800 hover:bg-gray-700 px-4 py-3 rounded-lg font-bold transition-colors border border-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="flex-1 bg-primary hover:bg-blue-600 px-4 py-3 rounded-lg font-bold transition-colors shadow-lg shadow-blue-500/20"
                >
                  {uploading ? 'Processing...' : 'Register'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
