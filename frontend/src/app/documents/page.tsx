'use client';
import { useEffect, useState, useCallback, useRef } from 'react';
import AppLayout from '@/components/AppLayout';
import DocumentTable, { Document } from '@/components/DocumentTable';
import UploadDocumentCard from '@/components/UploadDocumentCard';
import api from '@/lib/api';
import { Filter } from 'lucide-react';

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [filteredDocuments, setFilteredDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');

  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchDocuments = useCallback(async () => {
    try {
      const res = await api.get('/api/documents/');
      setDocuments(res.data);
    } catch (err) {
      console.error('Failed to fetch documents', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Poll single document status
  const checkPendingDocuments = useCallback(async () => {
    const pendingDocs = documents.filter(
      (doc) => doc.status === 'uploaded' || doc.status === 'processing'
    );

    if (pendingDocs.length === 0) {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
      return;
    }

    let updatedAny = false;
    const updatedDocs = await Promise.all(
      documents.map(async (doc) => {
        if (doc.status === 'uploaded' || doc.status === 'processing') {
          try {
            const res = await api.get(`/api/documents/${doc.id}`);
            if (res.data.status !== doc.status) {
              updatedAny = true;
            }
            return res.data;
          } catch (err) {
            console.error(`Failed to poll status for document ${doc.id}`, err);
            return doc;
          }
        }
        return doc;
      })
    );

    if (updatedAny) {
      setDocuments(updatedDocs);
    }
  }, [documents]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  // Handle polling trigger when there are pending documents
  useEffect(() => {
    const hasPending = documents.some(
      (doc) => doc.status === 'uploaded' || doc.status === 'processing'
    );

    if (hasPending && !pollIntervalRef.current) {
      pollIntervalRef.current = setInterval(() => {
        checkPendingDocuments();
      }, 3000); // Poll every 3 seconds
    } else if (!hasPending && pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    };
  }, [documents, checkPendingDocuments]);

  // Apply filters
  useEffect(() => {
    let result = [...documents];

    if (statusFilter !== 'all') {
      result = result.filter((doc) => doc.status === statusFilter);
    }

    if (typeFilter !== 'all') {
      result = result.filter((doc) => {
        const ext = doc.file_type.toLowerCase();
        if (typeFilter === 'pdf') return ext.includes('pdf');
        if (typeFilter === 'docx') return ext.includes('word') || ext.includes('docx');
        if (typeFilter === 'txt') return ext.includes('text/plain') || ext.includes('txt');
        if (typeFilter === 'md') return ext.includes('markdown') || ext.includes('md');
        return true;
      });
    }

    // Sort newest first
    result.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

    setFilteredDocuments(result);
  }, [documents, statusFilter, typeFilter]);

  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Documents Hub</h1>
          <p className="text-slate-500 mt-1">Manage, upload, and track indexing progress of your text corpora.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            
            {/* Filters bar */}
            <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex flex-wrap gap-4 items-center justify-between">
              <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
                <Filter className="w-4 h-4 text-slate-500" />
                <span>Filters</span>
              </div>
              <div className="flex flex-wrap gap-3">
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 bg-slate-50 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="all">All File Types</option>
                  <option value="pdf">PDF</option>
                  <option value="docx">DOCX</option>
                  <option value="txt">TXT</option>
                  <option value="md">Markdown</option>
                </select>

                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 bg-slate-50 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="all">All Statuses</option>
                  <option value="uploaded">Uploaded</option>
                  <option value="processing">Processing</option>
                  <option value="indexed">Indexed</option>
                  <option value="failed">Failed</option>
                </select>
              </div>
            </div>

            {loading ? (
              <div className="text-center text-slate-500 py-16 bg-white rounded-xl border border-slate-200 flex flex-col items-center justify-center space-y-3">
                <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                <span className="text-sm font-medium">Retrieving workspace documents...</span>
              </div>
            ) : (
              <DocumentTable documents={filteredDocuments} />
            )}
          </div>
          <div className="lg:col-span-1">
            <UploadDocumentCard onUploadSuccess={fetchDocuments} />
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
