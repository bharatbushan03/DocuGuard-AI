'use client';
import { FileText, Lock, Globe, Users, CheckCircle2, Loader2, AlertTriangle, FileUp } from 'lucide-react';

export interface Document {
  id: number;
  title: string;
  filename: string;
  file_type: string;
  access_level: string;
  status: 'uploaded' | 'processing' | 'indexed' | 'failed';
  created_at: string;
}

interface DocumentTableProps {
  documents: Document[];
}

export default function DocumentTable({ documents }: DocumentTableProps) {
  const getAccessIcon = (level: string) => {
    switch (level) {
      case 'private': return <Lock className="w-4 h-4 text-slate-500" />;
      case 'internal': return <Users className="w-4 h-4 text-blue-500" />;
      case 'public': return <Globe className="w-4 h-4 text-green-500" />;
      default: return <Lock className="w-4 h-4 text-slate-500" />;
    }
  };

  const getStatusBadge = (status: Document['status']) => {
    switch (status) {
      case 'indexed':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-50 text-green-800 border border-green-200">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Indexed
          </span>
        );
      case 'processing':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-800 border border-blue-200">
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            Processing
          </span>
        );
      case 'uploaded':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-50 text-slate-800 border border-slate-200">
            <FileUp className="w-3.5 h-3.5" />
            Uploaded
          </span>
        );
      case 'failed':
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-50 text-red-800 border border-red-200">
            <AlertTriangle className="w-3.5 h-3.5" />
            Failed
          </span>
        );
    }
  };

  const getFileExtensionLabel = (mimeType: string) => {
    if (mimeType.includes('pdf')) return 'PDF';
    if (mimeType.includes('word') || mimeType.includes('docx')) return 'DOCX';
    if (mimeType.includes('markdown') || mimeType.includes('md')) return 'MD';
    return 'TXT';
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">File Name</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Type</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Access Level</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Uploaded At</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-slate-200">
            {documents.map((doc) => (
              <tr key={doc.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
                      <FileText className="w-5 h-5" />
                    </div>
                    <span className="text-sm font-semibold text-slate-900 truncate max-w-xs">{doc.filename}</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600 font-medium">
                  {getFileExtensionLabel(doc.file_type)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-1.5 text-sm text-slate-600 capitalize">
                    {getAccessIcon(doc.access_level)}
                    {doc.access_level}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(doc.status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                  {new Date(doc.created_at).toLocaleString()}
                </td>
              </tr>
            ))}
            {documents.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-slate-400 text-sm">
                  <div className="flex flex-col items-center justify-center space-y-2">
                    <FileText className="h-8 w-8 text-slate-300" />
                    <p>No documents found matching the filters.</p>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
