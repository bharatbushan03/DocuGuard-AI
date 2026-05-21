'use client';
import { useEffect, useState } from 'react';
import AppLayout from '@/components/AppLayout';
import { syncUserRoleFromApi } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { 
  ShieldAlert, FileText, MessageSquare, Award, AlertTriangle, 
  Search, XCircle, ListFilter, TrendingUp, RefreshCw 
} from 'lucide-react';
import api from '@/lib/api';

interface Stats {
  total_documents: number;
  total_queries: number;
  avg_confidence: number;
  high_risk_queries_count: number;
  failed_documents_count: number;
  frequent_queries: { query: string; count: number }[];
  failed_documents: { id: number; filename: string; created_at: string }[];
}

interface QueryLog {
  id: number;
  user_id: number;
  query: string;
  answer: string;
  confidence_score: number;
  risk_level: string;
  latency_ms: number;
  created_at: string;
}

export default function AdminPage() {
  const router = useRouter();
  
  const [stats, setStats] = useState<Stats | null>(null);
  const [queryLogs, setQueryLogs] = useState<QueryLog[]>([]);
  const [highRiskLogs, setHighRiskLogs] = useState<QueryLog[]>([]);
  const [lowConfidenceLogs, setLowConfidenceLogs] = useState<QueryLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'all' | 'high-risk' | 'low-confidence'>('all');

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statsRes, logsRes, highRiskRes, lowConfRes] = await Promise.all([
        api.get('/api/admin/stats'),
        api.get('/api/admin/query-logs'),
        api.get('/api/admin/high-risk'),
        api.get('/api/admin/low-confidence')
      ]);

      setStats(statsRes.data);
      setQueryLogs(logsRes.data);
      setHighRiskLogs(highRiskRes.data);
      setLowConfidenceLogs(lowConfRes.data);
    } catch (err) {
      console.error('Failed to fetch admin data', err);
    } finally {
      setLoading(false);
    }
  };

  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    syncUserRoleFromApi().then((role) => {
      if (role !== 'admin') {
        router.push('/dashboard');
        return;
      }
      setAuthorized(true);
      fetchData();
    });
  }, [router]);

  if (!authorized) return null;

  const activeLogs = 
    activeTab === 'high-risk' ? highRiskLogs :
    activeTab === 'low-confidence' ? lowConfidenceLogs :
    queryLogs;

  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* Title and Refresh */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-50 text-red-600 rounded-xl border border-red-100">
              <ShieldAlert className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Compliance & Security Dashboard</h1>
              <p className="text-slate-500 mt-1">Review system telemetry, query logs, confidence metrics, and compliance violations.</p>
            </div>
          </div>
          <button 
            onClick={fetchData} 
            className="flex items-center gap-2 px-4 py-2 border border-slate-200 bg-white hover:bg-slate-50 text-sm font-semibold text-slate-700 rounded-lg shadow-sm transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {/* Loading Overlay */}
        {loading && !stats ? (
          <div className="text-center py-24 flex flex-col items-center justify-center space-y-4">
            <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <span className="text-sm font-semibold text-slate-600">Gathering administrative records...</span>
          </div>
        ) : (
          <>
            {/* Stat Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
                <div className="flex items-center justify-between text-slate-500 mb-3">
                  <span className="text-xs font-bold uppercase tracking-wider">Total Documents</span>
                  <FileText className="w-5 h-5 text-blue-500" />
                </div>
                <div className="text-2xl font-bold text-slate-900">{stats?.total_documents || 0}</div>
                <div className="text-xs text-red-600 mt-1 font-semibold flex items-center gap-1">
                  {stats?.failed_documents_count !== 0 && (
                    <>
                      <XCircle className="w-3.5 h-3.5" />
                      {stats?.failed_documents_count} Failed Indexing
                    </>
                  )}
                </div>
              </div>

              <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
                <div className="flex items-center justify-between text-slate-500 mb-3">
                  <span className="text-xs font-bold uppercase tracking-wider">Total Queries</span>
                  <MessageSquare className="w-5 h-5 text-indigo-500" />
                </div>
                <div className="text-2xl font-bold text-slate-900">{stats?.total_queries || 0}</div>
                <div className="text-xs text-slate-400 mt-1 font-medium">User prompts analyzed</div>
              </div>

              <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
                <div className="flex items-center justify-between text-slate-500 mb-3">
                  <span className="text-xs font-bold uppercase tracking-wider">Avg Confidence</span>
                  <Award className="w-5 h-5 text-emerald-500" />
                </div>
                <div className="text-2xl font-bold text-slate-900">
                  {stats?.avg_confidence ? (stats.avg_confidence * 100).toFixed(0) + '%' : '0%'}
                </div>
                <div className="text-xs text-slate-400 mt-1 font-medium">Target confidence threshold is 45%</div>
              </div>

              <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
                <div className="flex items-center justify-between text-slate-500 mb-3">
                  <span className="text-xs font-bold uppercase tracking-wider">High Risk Violations</span>
                  <AlertTriangle className="w-5 h-5 text-red-500" />
                </div>
                <div className={`text-2xl font-bold ${stats?.high_risk_queries_count && stats.high_risk_queries_count > 0 ? 'text-red-600' : 'text-slate-900'}`}>
                  {stats?.high_risk_queries_count || 0}
                </div>
                <div className="text-xs text-slate-400 mt-1 font-medium">Flagged PII or policy breaches</div>
              </div>
            </div>

            {/* Middle Section: Top Questions & Failed Documents */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Top Questions */}
              <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
                <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 flex items-center gap-1.5">
                  <TrendingUp className="w-4 h-4 text-blue-500" />
                  Most Frequently Asked Questions
                </h3>
                <div className="space-y-3">
                  {stats?.frequent_queries && stats.frequent_queries.length > 0 ? (
                    stats.frequent_queries.map((item, idx) => (
                      <div key={idx} className="flex justify-between items-center p-3 bg-slate-50 rounded-lg border border-slate-100">
                        <span className="text-xs font-semibold text-slate-700 truncate max-w-[80%]">"{item.query}"</span>
                        <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">{item.count} asks</span>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-6 text-slate-400 text-xs font-medium">No query history found.</div>
                  )}
                </div>
              </div>

              {/* Failed Documents */}
              <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
                <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 flex items-center gap-1.5">
                  <XCircle className="w-4 h-4 text-red-500" />
                  Failed Indexing Documents
                </h3>
                <div className="space-y-3">
                  {stats?.failed_documents && stats.failed_documents.length > 0 ? (
                    stats.failed_documents.map((doc, idx) => (
                      <div key={idx} className="flex justify-between items-center p-3 bg-red-50/30 rounded-lg border border-red-100">
                        <span className="text-xs font-semibold text-red-800 truncate max-w-[70%]">{doc.filename}</span>
                        <span className="text-[10px] font-medium text-slate-400">
                          {new Date(doc.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-6 text-slate-400 text-xs font-medium">No document parsing failures.</div>
                  )}
                </div>
              </div>

            </div>

            {/* Bottom Section: Query Telemetry Log */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="p-5 border-b border-slate-100 flex flex-wrap gap-4 items-center justify-between bg-slate-50/50">
                <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                  <ListFilter className="w-4 h-4 text-slate-500" />
                  Query Telemetry Logs
                </h3>
                
                {/* Tabs */}
                <div className="flex bg-slate-200/60 p-0.5 rounded-lg text-xs font-semibold">
                  <button
                    onClick={() => setActiveTab('all')}
                    className={`px-3 py-1.5 rounded-md transition-colors ${
                      activeTab === 'all' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    All Logs ({queryLogs.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('high-risk')}
                    className={`px-3 py-1.5 rounded-md transition-colors ${
                      activeTab === 'high-risk' ? 'bg-white text-red-700 shadow-sm' : 'text-slate-500 hover:text-red-600'
                    }`}
                  >
                    High Risk ({highRiskLogs.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('low-confidence')}
                    className={`px-3 py-1.5 rounded-md transition-colors ${
                      activeTab === 'low-confidence' ? 'bg-white text-amber-700 shadow-sm' : 'text-slate-500 hover:text-amber-600'
                    }`}
                  >
                    Low Confidence ({lowConfidenceLogs.length})
                  </button>
                </div>
              </div>

              {/* Table */}
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Timestamp</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Query / Question</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Answer Preview</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Risk Level</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Confidence</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Latency</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-slate-200">
                    {activeLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap text-xs text-slate-500">
                          {new Date(log.created_at).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-xs font-semibold text-slate-800 max-w-xs truncate">
                          {log.query}
                        </td>
                        <td className="px-6 py-4 text-xs text-slate-500 max-w-xs truncate">
                          {log.answer || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2.5 py-0.5 inline-flex text-[10px] leading-5 font-bold uppercase rounded-full border ${
                            log.risk_level === 'high' ? 'bg-red-50 text-red-700 border-red-200' :
                            log.risk_level === 'medium' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                            'bg-green-50 text-green-700 border-green-200'
                          }`}>
                            {log.risk_level}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {log.confidence_score !== null ? (
                            <span className={`text-xs font-bold ${log.confidence_score < 0.45 ? 'text-red-650' : 'text-slate-600'}`}>
                              {(log.confidence_score * 100).toFixed(0)}%
                            </span>
                          ) : (
                            <span className="text-xs text-slate-400">N/A</span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-xs text-slate-500">
                          {log.latency_ms ? `${log.latency_ms.toFixed(0)} ms` : 'N/A'}
                        </td>
                      </tr>
                    ))}
                    {activeLogs.length === 0 && (
                      <tr>
                        <td colSpan={6} className="px-6 py-12 text-center text-slate-400 text-sm">
                          <div className="flex flex-col items-center justify-center space-y-2">
                            <Search className="h-8 w-8 text-slate-350" />
                            <p>No queries found under the selected category.</p>
                          </div>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

      </div>
    </AppLayout>
  );
}
