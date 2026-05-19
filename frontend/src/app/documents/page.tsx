'use client';
import { useEffect, useState, useCallback } from 'react';
import AppLayout from '@/components/AppLayout';
import DocumentTable from '@/components/DocumentTable';
import UploadDocumentCard from '@/components/UploadDocumentCard';
import api from '@/lib/api';

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.get('/api/documents/');
      setDocuments(res.data);
    } catch (err) {
      console.error('Failed to fetch documents', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Documents</h1>
          <p className="text-slate-500 mt-1">Manage your uploaded files and view their indexing status.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            {loading ? (
              <div className="text-center text-slate-500 py-12 bg-white rounded-lg border border-slate-200">
                Loading documents...
              </div>
            ) : (
              <DocumentTable documents={documents} />
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
