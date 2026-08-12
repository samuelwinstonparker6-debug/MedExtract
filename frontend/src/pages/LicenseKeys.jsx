import React, { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import { KeyRound, User, Sparkles, Copy, Check, Search, ShieldCheck, Clock, RefreshCw } from 'lucide-react';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export default function LicenseKeys() {
  const [patientName, setPatientName] = useState('');
  const [generating, setGenerating] = useState(false);
  const [generatedKey, setGeneratedKey] = useState(null);  // { license_key, patient_name, created_at }
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');

  const [keys, setKeys] = useState([]);
  const [loadingKeys, setLoadingKeys] = useState(false);
  const [search, setSearch] = useState('');

  // ── Fetch history ─────────────────────────────────────────────────────────
  const fetchKeys = useCallback(async () => {
    setLoadingKeys(true);
    try {
      const res = await api.get(`/api/license-keys`);
      setKeys(res.data);
    } catch (e) {
      console.error('Failed to fetch license keys:', e);
    } finally {
      setLoadingKeys(false);
    }
  }, []);

  useEffect(() => { fetchKeys(); }, [fetchKeys]);

  // ── Generate ──────────────────────────────────────────────────────────────
  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!patientName.trim()) {
      setError('Please enter the patient\'s full name.');
      return;
    }
    setError('');
    setGenerating(true);
    setGeneratedKey(null);
    try {
      const res = await api.post(`/api/license-keys/generate`, {
        patient_name: patientName.trim(),
      });
      setGeneratedKey(res.data);
      await fetchKeys();
    } catch (e) {
      setError(e.response?.data?.detail || 'Generation failed. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  // ── Copy to clipboard ─────────────────────────────────────────────────────
  const handleCopy = () => {
    if (!generatedKey) return;
    navigator.clipboard.writeText(generatedKey.license_key);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // ── Filter history ────────────────────────────────────────────────────────
  const filteredKeys = keys.filter((k) => {
    const q = search.toLowerCase();
    return (
      k.license_key.toLowerCase().includes(q) ||
      k.patient_name.toLowerCase().includes(q)
    );
  });

  return (
    <div className="flex flex-col gap-8 h-full">

      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <div className="relative overflow-hidden bg-surface border border-gray-700 rounded-2xl p-8">
        {/* Decorative background glow */}
        <div className="absolute -top-10 -right-10 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-10 -left-10 w-48 h-48 bg-yellow-400/5 rounded-full blur-2xl pointer-events-none" />
        <div className="relative flex items-center gap-5">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-500 to-yellow-400 flex items-center justify-center shadow-lg shadow-amber-500/30 flex-shrink-0">
            <KeyRound className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-black tracking-tight mb-1">License Key Generator</h1>
            <p className="text-gray-400 text-sm leading-relaxed max-w-xl">
              Generate a unique <span className="font-mono text-amber-400 font-bold">AAaANN</span> license key bonded to a patient's name.
              Each key is stored securely and verified automatically when documents are uploaded.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">

        {/* ── Generate Panel (2/5) ─────────────────────────────────────────── */}
        <div className="lg:col-span-2 flex flex-col gap-4">
          <div className="bg-surface border border-gray-700 rounded-2xl p-6">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-400" />
              Generate New Key
            </h2>

            <form onSubmit={handleGenerate} className="flex flex-col gap-4">
              <div>
                <label htmlFor="patient-name-input" className="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">
                  Patient Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    id="patient-name-input"
                    type="text"
                    value={patientName}
                    onChange={(e) => { setPatientName(e.target.value); setError(''); }}
                    placeholder="e.g. Rajesh Kumar Sharma"
                    className="w-full bg-background border border-gray-700 rounded-xl pl-10 pr-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500/30 transition-all"
                    autoComplete="off"
                  />
                </div>
              </div>

              {error && (
                <div className="bg-red-900/30 border border-red-500/30 text-red-400 text-sm px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              <button
                type="submit"
                id="generate-license-key-btn"
                disabled={generating}
                className="w-full py-3 rounded-xl font-bold text-sm tracking-wide transition-all shadow-lg
                  bg-gradient-to-r from-amber-500 to-yellow-400 text-gray-900
                  hover:from-amber-400 hover:to-yellow-300
                  disabled:opacity-50 disabled:cursor-not-allowed
                  flex items-center justify-center gap-2"
              >
                {generating ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Generating…
                  </>
                ) : (
                  <>
                    <KeyRound className="w-4 h-4" />
                    Generate Key
                  </>
                )}
              </button>
            </form>
          </div>

          {/* ── Result Card ──────────────────────────────────────────────── */}
          {generatedKey && (
            <div
              className="bg-surface border border-amber-500/40 rounded-2xl p-6 shadow-xl shadow-amber-500/10 animate-fadeIn"
              style={{ animation: 'fadeSlideIn 0.4s ease forwards' }}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-amber-400 uppercase tracking-widest flex items-center gap-1">
                  <ShieldCheck className="w-4 h-4" />
                  Key Generated
                </span>
                <button
                  onClick={handleCopy}
                  id="copy-license-key-btn"
                  title="Copy to clipboard"
                  className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 border border-gray-700 hover:border-amber-500/50 transition-all font-medium"
                >
                  {copied ? (
                    <><Check className="w-3.5 h-3.5 text-emerald-400" /> Copied!</>
                  ) : (
                    <><Copy className="w-3.5 h-3.5 text-gray-400" /> Copy</>
                  )}
                </button>
              </div>

              {/* Big key display */}
              <div className="mt-3 mb-4 text-center">
                <span className="font-mono text-5xl font-black tracking-[0.25em] bg-gradient-to-r from-amber-400 to-yellow-300 bg-clip-text text-transparent select-all">
                  {generatedKey.license_key}
                </span>
              </div>

              <div className="bg-background/60 rounded-xl px-4 py-3 text-sm text-gray-300 flex items-center gap-2">
                <User className="w-4 h-4 text-amber-400 flex-shrink-0" />
                <span className="font-medium">{generatedKey.patient_name}</span>
              </div>
              <p className="mt-2 text-xs text-gray-600 text-center">
                This key is permanently bonded to this patient name.
              </p>
            </div>
          )}
        </div>

        {/* ── History Table (3/5) ──────────────────────────────────────────── */}
        <div className="lg:col-span-3 bg-surface border border-gray-700 rounded-2xl p-6 flex flex-col gap-4">
          <div className="flex items-center justify-between flex-wrap gap-3">
            <h2 className="text-lg font-bold flex items-center gap-2">
              <Clock className="w-5 h-5 text-gray-400" />
              All Generated Keys
              <span className="text-xs text-gray-600 font-normal">({keys.length} total)</span>
            </h2>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                id="license-key-search"
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search keys or names…"
                className="bg-background border border-gray-700 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-amber-500 transition-all w-52"
              />
            </div>
          </div>

          {loadingKeys ? (
            <div className="flex-1 flex items-center justify-center py-16 text-gray-500">
              <RefreshCw className="w-6 h-6 animate-spin mr-2" />
              Loading…
            </div>
          ) : filteredKeys.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center py-16 text-gray-600">
              <KeyRound className="w-12 h-12 mb-3 opacity-30" />
              <p className="text-sm">{search ? 'No matching keys found.' : 'No keys generated yet.'}</p>
            </div>
          ) : (
            <div className="overflow-x-auto rounded-xl border border-gray-800">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-900/60 text-gray-500 text-xs uppercase tracking-widest">
                    <th className="text-left px-4 py-3 font-semibold">#</th>
                    <th className="text-left px-4 py-3 font-semibold">Key</th>
                    <th className="text-left px-4 py-3 font-semibold">Patient Name</th>
                    <th className="text-left px-4 py-3 font-semibold">Generated</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredKeys.map((k, idx) => (
                    <tr
                      key={k.id}
                      className={`border-t border-gray-800/60 transition-colors hover:bg-gray-800/40 ${
                        generatedKey?.license_key === k.license_key ? 'bg-amber-900/10' : ''
                      }`}
                    >
                      <td className="px-4 py-3 text-gray-600 font-mono text-xs">{k.id}</td>
                      <td className="px-4 py-3">
                        <span className="font-mono font-bold text-amber-400 tracking-widest bg-amber-500/10 px-2 py-1 rounded-md text-base">
                          {k.license_key}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-200 font-medium">{k.patient_name}</td>
                      <td className="px-4 py-3 text-gray-500 text-xs whitespace-nowrap">
                        {k.created_at ? new Date(k.created_at).toLocaleString() : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Inline keyframe for the result card animation */}
      <style>{`
        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(12px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
