import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid, Cell } from 'recharts';
import { Activity, Clock, CheckCircle, FileText } from 'lucide-react';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const [statsRes, alertsRes] = await Promise.all([
        api.get('/api/v2/analytics/summary'),
        api.get('/api/v2/documents/fraud/alerts')
      ]);
      setData({ ...statsRes.data, alerts: alertsRes.data });
    } catch (error) {
      console.error("Error fetching analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading) {
    return <div className="flex justify-center items-center h-64"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div></div>;
  }

  if (!data) {
    return (
      <div className="text-center text-red-400 p-8 glass-panel rounded-xl flex flex-col items-center gap-4">
        <div>Failed to load analytics</div>
        <button 
          onClick={fetchAnalytics}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors cursor-pointer"
        >
          Retry Loading
        </button>
      </div>
    );
  }

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-primary">Analytics Overview</h1>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-panel p-6 rounded-xl flex flex-col gap-2 hover:scale-105 transition-transform duration-300">
          <div className="flex items-center gap-3 text-gray-400 mb-1">
            <FileText className="text-blue-400" /> Total Documents
          </div>
          <div className="text-4xl font-bold">{data.total_documents}</div>
        </div>
        
        <div className="glass-panel p-6 rounded-xl flex flex-col gap-2 hover:scale-105 transition-transform duration-300">
          <div className="flex items-center gap-3 text-gray-400 mb-1">
            <CheckCircle className="text-green-400" /> Avg Confidence
          </div>
          <div className="text-4xl font-bold">{(data.average_confidence * 100).toFixed(1)}%</div>
        </div>
        
        <div className="glass-panel p-6 rounded-xl flex flex-col gap-2 hover:scale-105 transition-transform duration-300 glow-amber border-amber-500/30">
          <div className="flex items-center gap-3 text-amber-400 mb-1 font-semibold">
            <Activity className="text-amber-400" /> Suspicious (Amber)
          </div>
          <div className="text-4xl font-bold text-amber-500">{data.fraud_stats?.AMBER || 0}</div>
        </div>
        
        <div className="glass-panel p-6 rounded-xl flex flex-col gap-2 hover:scale-105 transition-transform duration-300 glow-red border-red-500/30">
          <div className="flex items-center gap-3 text-red-400 mb-1 font-semibold">
            <Activity className="text-red-400 animate-pulse-subtle" /> High Fraud Risk (Red)
          </div>
          <div className="text-4xl font-bold text-red-500">{data.fraud_stats?.RED || 0}</div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Document Types Bar Chart */}
        <div className="glass-panel p-6 rounded-xl hover:-translate-y-1 transition-transform duration-300">
          <h2 className="text-lg font-bold mb-4 text-gray-200">Documents by Type</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.documents_by_type}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis dataKey="name" stroke="#a1a1aa" />
                <YAxis stroke="#a1a1aa" />
                <Tooltip cursor={{fill: 'rgba(255,255,255,0.02)'}} contentStyle={{backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px'}} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {data.documents_by_type.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Fraud Risk Breakdown Chart */}
        <div className="glass-panel p-6 rounded-xl hover:-translate-y-1 transition-transform duration-300">
          <h2 className="text-lg font-bold mb-4 text-gray-200">Fraud Risk Distribution</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={[
                { name: 'Safe', count: data.fraud_stats?.NONE || 0, fill: '#10b981' },
                { name: 'Amber', count: data.fraud_stats?.AMBER || 0, fill: '#f59e0b' },
                { name: 'Red', count: data.fraud_stats?.RED || 0, fill: '#ef4444' }
              ]}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis dataKey="name" stroke="#a1a1aa" />
                <YAxis stroke="#a1a1aa" />
                <Tooltip cursor={{fill: 'rgba(255,255,255,0.02)'}} contentStyle={{backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px'}} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  <Cell fill="#10b981" />
                  <Cell fill="#f59e0b" />
                  <Cell fill="#ef4444" />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Volume Over Time Line Chart */}
        <div className="glass-panel p-6 rounded-xl hover:-translate-y-1 transition-transform duration-300">
          <h2 className="text-lg font-bold mb-4 text-gray-200">Processing Volume (7 Days)</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.volume_over_time}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis dataKey="date" stroke="#a1a1aa" />
                <YAxis stroke="#a1a1aa" />
                <Tooltip contentStyle={{backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px'}} />
                <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={3} dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }} activeDot={{ r: 6, fill: '#60a5fa' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Fraud Alerts Section */}
      <div className="glass-panel p-6 rounded-xl mt-6">
        <h2 className="text-xl font-bold mb-4 text-red-400 flex items-center gap-2">
          <Activity className="w-6 h-6" /> Fraud Alerts & Suspicious Templates
        </h2>
        
        {(!data.alerts || data.alerts.length === 0) ? (
          <div className="text-center p-8 border border-dashed border-gray-700 rounded-lg text-gray-500">
            <CheckCircle className="w-12 h-12 mx-auto mb-3 text-green-500/50" />
            <p>No suspicious template matches detected.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-gray-700 text-gray-400">
                  <th className="p-3">Doc #1</th>
                  <th className="p-3">Provider #1</th>
                  <th className="p-3">Doc #2</th>
                  <th className="p-3">Provider #2</th>
                  <th className="p-3">Similarity</th>
                  <th className="p-3">Risk Level</th>
                  <th className="p-3">Date Detected</th>
                </tr>
              </thead>
              <tbody>
                {data.alerts.map((alert) => (
                  <tr key={alert.id} className="border-b border-gray-800 hover:bg-gray-800/50">
                    <td className="p-3">#{alert.document_id_1}</td>
                    <td className="p-3">{alert.provider_name_1 || 'Unknown'}</td>
                    <td className="p-3">#{alert.document_id_2}</td>
                    <td className="p-3">{alert.provider_name_2 || 'Unknown'}</td>
                    <td className="p-3 font-mono">{(alert.similarity_score * 100).toFixed(1)}%</td>
                    <td className="p-3">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${
                        alert.flag_level === 'RED' ? 'bg-red-500/20 text-red-400 border border-red-500/50' : 'bg-amber-500/20 text-amber-400 border border-amber-500/50'
                      }`}>
                        {alert.flag_level}
                      </span>
                    </td>
                    <td className="p-3 text-sm text-gray-500">
                      {new Date(alert.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}
