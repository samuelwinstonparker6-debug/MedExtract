import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileText, AlertTriangle, CheckCircle, Database, Activity, RefreshCw } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import { api } from '@/lib/api';

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [templateCount, setTemplateCount] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsRes, alertsRes, tplRes] = await Promise.all([
        api.get('/api/v2/analytics/summary'),
        api.get('/api/v2/documents/fraud/alerts'),
        api.get('/api/v2/provider-templates')
      ]);

      let totalTpls = 0;
      if (tplRes.data) {
        Object.values(tplRes.data).forEach((arr: any) => {
          if (Array.isArray(arr)) totalTpls += arr.length;
        });
      }

      setData({
        ...statsRes.data,
        alerts: alertsRes.data || []
      });
      setTemplateCount(totalTpls);
    } catch (err: any) {
      console.error("Error fetching analytics:", err);
      setError("Unable to connect to backend analytics service.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="p-8 max-w-7xl mx-auto flex flex-col justify-center items-center h-64 gap-4">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <p className="text-slate-500 font-medium">Loading real-time metrics...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 max-w-7xl mx-auto">
        <div className="bg-red-50 border border-red-200 text-red-700 p-6 rounded-xl text-center flex flex-col items-center gap-4">
          <AlertTriangle className="w-10 h-10 text-red-500" />
          <div>
            <h3 className="font-bold text-lg">Metrics Service Unavailable</h3>
            <p className="text-sm mt-1">{error || "Failed to load dashboard data."}</p>
          </div>
          <button 
            onClick={fetchAnalytics}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm font-medium"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  const redCount = data.fraud_stats?.RED || 0;
  const amberCount = data.fraud_stats?.AMBER || 0;
  const greenCount = data.fraud_stats?.NONE || (data.total_documents - redCount - amberCount);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Overview</h1>
          <p className="text-slate-500 mt-1">Real-time template matching & fraud risk intelligence.</p>
        </div>
        <Badge variant="success" className="px-3 py-1 text-sm bg-emerald-100 text-emerald-800 border-emerald-300">
          Backend Connected
        </Badge>
      </div>

      {/* KPI Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-500">Total Documents</CardTitle>
            <FileText className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">{data.total_documents}</div>
            <p className="text-xs text-slate-500 mt-1">Avg Confidence: {(data.average_confidence * 100).toFixed(0)}%</p>
          </CardContent>
        </Card>

        <Card className="border-red-200 bg-red-50/20">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-red-800">High Fraud Risk (RED)</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{redCount}</div>
            <p className="text-xs text-red-600/80 mt-1">Requires investigator review</p>
          </CardContent>
        </Card>

        <Card className="border-amber-200 bg-amber-50/20">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-amber-800">Suspicious (AMBER)</CardTitle>
            <Activity className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-amber-600">{amberCount}</div>
            <p className="text-xs text-amber-600/80 mt-1">Potential structural anomaly</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-500">Provider Templates</CardTitle>
            <Database className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">{templateCount}</div>
            <p className="text-xs text-slate-500 mt-1">Registered reference templates</p>
          </CardContent>
        </Card>
      </div>

      {/* Visual Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Processing Volume */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg">Processing Volume (Last 7 Days)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[280px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.volume_over_time || []}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} allowDecimals={false} />
                  <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                  <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={3} dot={{ fill: '#3b82f6', r: 4 }} name="Documents Ingested" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Fraud Risk Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Fraud Risk Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[280px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={[
                  { name: 'Low Risk', count: greenCount, color: '#10b981' },
                  { name: 'Amber', count: amberCount, color: '#f59e0b' },
                  { name: 'Red Risk', count: redCount, color: '#ef4444' }
                ]}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} allowDecimals={false} />
                  <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0' }} />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                    <Cell fill="#10b981" />
                    <Cell fill="#f59e0b" />
                    <Cell fill="#ef4444" />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Alerts */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Activity className="w-5 h-5 text-red-500" />
            Flagged Case Alerts (RED & AMBER)
          </CardTitle>
          <Badge variant="outline" className="text-xs">{data.alerts?.length || 0} Cases Requiring Review</Badge>
        </CardHeader>
        <CardContent>
          {!data.alerts || data.alerts.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              <CheckCircle className="w-10 h-10 mx-auto mb-2 text-emerald-500/60" />
              <p className="text-sm font-medium">No flagged cases currently in the investigation queue.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {data.alerts.slice(0, 5).map((doc: any) => (
                <div key={doc.id} className="flex items-center justify-between p-3 border border-slate-100 rounded-lg bg-slate-50/50 hover:bg-slate-100/50 transition-colors">
                  <div>
                    <span className="font-semibold text-slate-900 text-sm">Document #{doc.id}</span>
                    <span className="text-xs text-slate-500 ml-3 capitalize">Type: {doc.document_type || doc.source_type}</span>
                    {doc.fraud_flags && doc.fraud_flags.length > 0 && (
                      <p className="text-xs text-slate-600 mt-0.5 line-clamp-1">{doc.fraud_flags[0]}</p>
                    )}
                  </div>
                  <Badge variant={doc.fraud_status === 'RED' ? 'destructive' : 'warning'} className="text-xs font-bold px-2.5 py-0.5">
                    {doc.fraud_status === 'RED' ? 'HIGH RISK' : 'SUSPICIOUS'}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

