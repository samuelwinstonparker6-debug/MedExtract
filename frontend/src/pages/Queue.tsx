import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Search, Filter, Eye, Trash2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api";

export default function Queue() {
  const navigate = useNavigate();
  const [queue, setQueue] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchQueue = async () => {
    setIsLoading(true);
    try {
      const response = await api.get('/api/v2/documents/fraud/alerts');
      setQueue(response.data);
    } catch (error) {
      console.error('Error fetching fraud queue:', error);
      setQueue([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const handleDelete = async (documentId) => {
    if (!window.confirm(`Delete fraud queue record #${documentId}? This will remove it permanently.`)) {
      return;
    }

    try {
      await api.delete(`/api/v2/documents/${documentId}`);
      setQueue((prev) => prev.filter((item) => item.id !== documentId));
    } catch (error) {
      console.error('Failed to delete fraud queue record:', error);
      alert('Unable to delete this record. Please try again.');
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Fraud Investigation Queue</h1>
          <p className="text-slate-500 mt-1">Review flagged anomalies and structural similarities.</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="gap-2"><Filter size={16} /> Filter</Button>
          <Button variant="outline" className="gap-2"><Search size={16} /> Search</Button>
        </div>
      </div>

      <Card>
        <CardHeader className="border-b border-slate-100 bg-slate-50/50 pb-4">
          <CardTitle>Needs Attention (RED & AMBER)</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-12 text-center text-slate-500">Loading fraud queue...</div>
          ) : (
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-100">
                <tr>
                  <th className="px-6 py-4 font-medium">Document ID</th>
                  <th className="px-6 py-4 font-medium">Claimed Provider</th>
                  <th className="px-6 py-4 font-medium">Date</th>
                  <th className="px-6 py-4 font-medium">Matched Template</th>
                  <th className="px-6 py-4 font-medium">Risk Score</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                  <th className="px-6 py-4 font-medium text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {queue.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-slate-500">
                      No fraud records found.
                    </td>
                  </tr>
                ) : (
                  queue.map((item) => (
                    <tr key={item.id} className="border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4 font-medium text-slate-900">#{item.id}</td>
                      <td className="px-6 py-4">{item.source_type || 'Unknown'}</td>
                      <td className="px-6 py-4 text-slate-500">{item.upload_timestamp ? new Date(item.upload_timestamp).toLocaleDateString() : '-'}</td>
                      <td className="px-6 py-4 text-slate-500 font-mono text-xs">{item.document_type || 'Unknown'}</td>
                      <td className="px-6 py-4">
                        <Badge variant={item.fraud_status === 'RED' ? 'destructive' : 'warning'} className="font-bold px-2.5 py-1">
                          {item.fraud_score ? (item.fraud_score * 100).toFixed(0) + '%' : ''} {item.fraud_status === 'RED' ? 'HIGH RISK' : item.fraud_status === 'AMBER' ? 'SUSPICIOUS' : 'LOW RISK'}
                        </Badge>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center gap-1.5 py-1 px-2 rounded-md text-xs font-medium bg-slate-100 text-slate-600">
                          {item.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right flex items-center justify-end gap-2">
                        <Button
                          size="sm"
                          onClick={() => navigate(`/similarity/${item.id}`)}
                          className="gap-2"
                        >
                          <Eye size={14} /> Investigate
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleDelete(item.id)}
                          className="gap-2"
                        >
                          <Trash2 size={14} /> Delete
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
